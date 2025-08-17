"""
Google Calendar analysis module for pattern detection and time usage analysis
"""

import os
import pickle
import logging
from datetime import datetime, timedelta, time as dt_time
from typing import List, Dict, Any, Tuple
from collections import defaultdict, Counter

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
import pytz
from dateutil import parser

logger = logging.getLogger(__name__)

class CalendarAnalyzer:
    """Analyzes Google Calendar events for patterns and time usage."""
    
    def __init__(self, config):
        self.config = config
        self.service = None
        self.timezone = pytz.timezone(config.timezone)
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Calendar API."""
        creds = None
        
        # Load existing token
        if os.path.exists(self.config.google_token_path):
            with open(self.config.google_token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.config.google_credentials_path):
                    raise FileNotFoundError(
                        f"Google credentials file not found: {self.config.google_credentials_path}\n"
                        "Please download the credentials.json file from Google Cloud Console."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.google_credentials_path, self.config.get_scopes())
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.config.google_token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('calendar', 'v3', credentials=creds)
        logger.info("Successfully authenticated with Google Calendar API")
    
    def get_events(self, start_date, end_date) -> List[Dict]:
        """Retrieve calendar events for the specified date range."""
        try:
            # Convert dates to RFC3339 format
            start_datetime = datetime.combine(start_date, dt_time.min).replace(tzinfo=self.timezone)
            end_datetime = datetime.combine(end_date, dt_time.max).replace(tzinfo=self.timezone)
            
            start_iso = start_datetime.isoformat()
            end_iso = end_datetime.isoformat()
            
            logger.info(f"Fetching events from {start_iso} to {end_iso}")
            
            events_result = self.service.events().list(
                calendarId=self.config.calendar_id,
                timeMin=start_iso,
                timeMax=end_iso,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} events")
            
            return events
            
        except Exception as e:
            logger.error(f"Error fetching calendar events: {str(e)}")
            return []
    
    def _parse_event_time(self, event_time_data) -> datetime:
        """Parse event time from Google Calendar API response."""
        if 'dateTime' in event_time_data:
            return parser.parse(event_time_data['dateTime'])
        elif 'date' in event_time_data:
            # All-day event
            date_str = event_time_data['date']
            return datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=self.timezone)
        else:
            raise ValueError("No valid time found in event data")
    
    def _categorize_event(self, event: Dict) -> str:
        """Categorize an event based on its title and description."""
        title = event.get('summary', '').lower()
        description = event.get('description', '').lower()
        text_to_analyze = f"{title} {description}"
        
        for category, keywords in self.config.meeting_keywords.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                return category
        
        # Check attendee count for meeting size categorization
        attendees = event.get('attendees', [])
        if len(attendees) > 10:
            return 'large_meeting'
        elif len(attendees) > 3:
            return 'team_meeting'
        elif len(attendees) == 2:
            return 'small_meeting'
        
        return 'other'
    
    def _calculate_duration(self, event: Dict) -> timedelta:
        """Calculate the duration of an event."""
        try:
            start_time = self._parse_event_time(event['start'])
            end_time = self._parse_event_time(event['end'])
            return end_time - start_time
        except Exception as e:
            logger.warning(f"Could not calculate duration for event: {event.get('summary', 'Unknown')}")
            return timedelta(0)
    
    def _is_working_hours(self, event_start: datetime) -> bool:
        """Check if an event is during working hours."""
        hour = event_start.hour
        return self.config.working_hours_start <= hour < self.config.working_hours_end
    
    def analyze_week(self, events: List[Dict], start_date, end_date) -> Dict[str, Any]:
        """Analyze a week's worth of events for patterns and time usage."""
        if not events:
            return {
                'total_events': 0,
                'total_meeting_time': timedelta(0),
                'daily_breakdown': {},
                'category_breakdown': {},
                'time_usage': {},
                'patterns': {},
                'insights': []
            }
        
        # Initialize analysis data
        daily_stats = defaultdict(lambda: {
            'events': 0, 
            'meeting_time': timedelta(0),
            'categories': defaultdict(int)
        })
        category_stats = defaultdict(lambda: {
            'count': 0, 
            'total_time': timedelta(0)
        })
        hourly_distribution = defaultdict(int)
        
        total_meeting_time = timedelta(0)
        working_hours_time = timedelta(0)
        after_hours_time = timedelta(0)
        
        # Process each event
        for event in events:
            try:
                # Skip declined events
                if event.get('status') == 'cancelled':
                    continue
                
                # Skip private events if configured
                if not self.config.include_private_events and event.get('visibility') == 'private':
                    continue
                
                start_time = self._parse_event_time(event['start'])
                duration = self._calculate_duration(event)
                category = self._categorize_event(event)
                
                # Daily breakdown
                day_key = start_time.strftime('%A')
                daily_stats[day_key]['events'] += 1
                daily_stats[day_key]['meeting_time'] += duration
                daily_stats[day_key]['categories'][category] += 1
                
                # Category breakdown
                category_stats[category]['count'] += 1
                category_stats[category]['total_time'] += duration
                
                # Time distribution
                hour = start_time.hour
                hourly_distribution[hour] += 1
                
                # Working hours vs after hours
                total_meeting_time += duration
                if self._is_working_hours(start_time):
                    working_hours_time += duration
                else:
                    after_hours_time += duration
                
            except Exception as e:
                logger.warning(f"Error processing event: {str(e)}")
                continue
        
        # Calculate insights
        insights = self._generate_insights(
            len(events), daily_stats, category_stats, 
            working_hours_time, after_hours_time, hourly_distribution
        )
        
        return {
            'period': f"{start_date} to {end_date}",
            'total_events': len(events),
            'total_meeting_time': total_meeting_time,
            'working_hours_time': working_hours_time,
            'after_hours_time': after_hours_time,
            'daily_breakdown': dict(daily_stats),
            'category_breakdown': dict(category_stats),
            'hourly_distribution': dict(hourly_distribution),
            'patterns': self._identify_patterns(daily_stats, category_stats),
            'insights': insights
        }
    
    def _generate_insights(self, total_events, daily_stats, category_stats, 
                          working_hours_time, after_hours_time, hourly_distribution) -> List[str]:
        """Generate insights based on the analysis."""
        insights = []
        
        # Meeting load insights
        if total_events > 25:
            insights.append("📅 Heavy meeting week - consider blocking focus time")
        elif total_events < 5:
            insights.append("📅 Light meeting week - good for deep work")
        
        # Work-life balance insights
        total_time = working_hours_time + after_hours_time
        if total_time > timedelta(0):
            after_hours_percentage = (after_hours_time / total_time) * 100
            if after_hours_percentage > 20:
                insights.append(f"⏰ {after_hours_percentage:.1f}% of meetings were outside working hours")
        
        # Meeting type insights
        if category_stats:
            top_category = max(category_stats.items(), key=lambda x: x[1]['count'])
            insights.append(f"🎯 Most common meeting type: {top_category[0]} ({top_category[1]['count']} meetings)")
        
        # Daily distribution insights
        if daily_stats:
            busiest_day = max(daily_stats.items(), key=lambda x: x[1]['events'])
            if busiest_day[1]['events'] > 6:
                insights.append(f"📊 Busiest day: {busiest_day[0]} with {busiest_day[1]['events']} meetings")
        
        # Peak hours
        if hourly_distribution:
            peak_hour = max(hourly_distribution.items(), key=lambda x: x[1])
            insights.append(f"🕐 Peak meeting hour: {peak_hour[0]}:00 ({peak_hour[1]} meetings)")
        
        return insights
    
    def _identify_patterns(self, daily_stats, category_stats) -> Dict[str, Any]:
        """Identify patterns in meeting behavior."""
        patterns = {}
        
        # Daily patterns
        day_counts = {day: stats['events'] for day, stats in daily_stats.items()}
        if day_counts:
            patterns['busiest_day'] = max(day_counts.items(), key=lambda x: x[1])
            patterns['lightest_day'] = min(day_counts.items(), key=lambda x: x[1])
        
        # Meeting type patterns
        if category_stats:
            patterns['dominant_meeting_type'] = max(
                category_stats.items(), 
                key=lambda x: x[1]['count']
            )[0]
        
        return patterns
    
    def summarize_upcoming_week(self, events: List[Dict], start_date, end_date) -> Dict[str, Any]:
        """Generate a summary of upcoming week's events."""
        if not events:
            return {
                'total_events': 0,
                'daily_schedule': {},
                'key_meetings': [],
                'focus_opportunities': []
            }
        
        daily_schedule = defaultdict(list)
        key_meetings = []
        
        for event in events:
            try:
                if event.get('status') == 'cancelled':
                    continue
                
                start_time = self._parse_event_time(event['start'])
                duration = self._calculate_duration(event)
                
                day_key = start_time.strftime('%A, %B %d')
                time_str = start_time.strftime('%H:%M')
                
                event_info = {
                    'title': event.get('summary', 'No title'),
                    'time': time_str,
                    'duration': str(duration).split('.')[0],  # Remove microseconds
                    'attendees_count': len(event.get('attendees', []))
                }
                
                daily_schedule[day_key].append(event_info)
                
                # Identify key meetings (long duration or many attendees)
                if duration > timedelta(hours=1) or len(event.get('attendees', [])) > 5:
                    key_meetings.append({
                        'title': event.get('summary', 'No title'),
                        'day': day_key,
                        'time': time_str,
                        'reason': 'Long duration' if duration > timedelta(hours=1) else 'Many attendees'
                    })
                
            except Exception as e:
                logger.warning(f"Error processing upcoming event: {str(e)}")
                continue
        
        # Identify focus opportunities (days with fewer meetings)
        focus_opportunities = []
        for day, meetings in daily_schedule.items():
            if len(meetings) <= 2:
                focus_opportunities.append(f"{day} - Good for focus work ({len(meetings)} meetings)")
        
        return {
            'period': f"{start_date} to {end_date}",
            'total_events': len(events),
            'daily_schedule': dict(daily_schedule),
            'key_meetings': key_meetings[:self.config.max_upcoming_events],
            'focus_opportunities': focus_opportunities
        } 