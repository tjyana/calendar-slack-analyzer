"""
Slack integration module for sending calendar analysis reports
"""

import logging
from datetime import timedelta
from typing import Dict, Any, List

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

class SlackReporter:
    """Handles formatting and sending calendar analysis reports to Slack."""
    
    def __init__(self, config):
        self.config = config
        self.client = WebClient(token=config.slack_token)
    
    def _format_duration(self, duration: timedelta) -> str:
        """Format a timedelta object into a readable string."""
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
    
    def _create_past_week_section(self, analysis: Dict[str, Any]) -> List[Dict]:
        """Create Slack blocks for past week analysis."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📊 Past Week Analysis"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Overview section
        total_time_str = self._format_duration(analysis['total_meeting_time'])
        working_hours_str = self._format_duration(analysis['working_hours_time'])
        after_hours_str = self._format_duration(analysis['after_hours_time'])
        
        overview_text = (
            f"*Period:* {analysis['period']}\n"
            f"*Total Meetings:* {analysis['total_events']}\n"
            f"*Total Meeting Time:* {total_time_str}\n"
            f"*Working Hours:* {working_hours_str}\n"
            f"*After Hours:* {after_hours_str}"
        )
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": overview_text
            }
        })
        
        # Daily breakdown
        if analysis['daily_breakdown']:
            daily_text = "*Daily Breakdown:*\n"
            for day, stats in analysis['daily_breakdown'].items():
                time_str = self._format_duration(stats['meeting_time'])
                daily_text += f"• {day}: {stats['events']} meetings ({time_str})\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": daily_text
                }
            })
        
        # Meeting categories
        if analysis['category_breakdown']:
            category_text = "*Meeting Types:*\n"
            for category, stats in analysis['category_breakdown'].items():
                time_str = self._format_duration(stats['total_time'])
                category_text += f"• {category.replace('_', ' ').title()}: {stats['count']} meetings ({time_str})\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": category_text
                }
            })
        
        # Insights
        if analysis['insights']:
            insights_text = "*Key Insights:*\n"
            for insight in analysis['insights']:
                insights_text += f"• {insight}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": insights_text
                }
            })
        
        return blocks
    
    def _create_upcoming_week_section(self, summary: Dict[str, Any]) -> List[Dict]:
        """Create Slack blocks for upcoming week summary."""
        blocks = [
            {
                "type": "divider"
            },
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📅 Upcoming Week Preview"
                }
            },
            {
                "type": "divider"
            }
        ]
        
        # Add AI summary if enabled
        if getattr(self.config, 'upcoming_ai_summary_enabled', True):
            ai_summary = self._generate_upcoming_ai_summary(summary)
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🔮 *Week Ahead Summary*\n{ai_summary}"
                }
            })
            blocks.append({
                "type": "divider"
            })
        
        # Overview
        overview_text = (
            f"*Period:* {summary['period']}\n"
            f"*Total Scheduled Meetings:* {summary['total_events']}"
        )
        
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": overview_text
            }
        })
        
        # Daily schedule (show only if AI summary is disabled or as a brief overview)
        if summary['daily_schedule'] and not getattr(self.config, 'upcoming_ai_summary_enabled', True):
            # Full detailed schedule when AI summary is disabled
            schedule_text = "*This Week's Schedule:*\n"
            day_count = 0
            for day, meetings in summary['daily_schedule'].items():
                if day_count >= 3:  # Limit to first 3 days to avoid long messages
                    remaining_days = len(summary['daily_schedule']) - day_count
                    if remaining_days > 0:
                        schedule_text += f"... and {remaining_days} more days\n"
                    break
                
                schedule_text += f"\n*{day}* ({len(meetings)} meetings):\n"
                for meeting in meetings[:3]:  # Show max 3 meetings per day
                    schedule_text += f"  • {meeting['time']} - {meeting['title']} ({meeting['duration']})\n"
                
                if len(meetings) > 3:
                    schedule_text += f"  ... and {len(meetings) - 3} more meetings\n"
                
                day_count += 1
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": schedule_text
                }
            })
        elif summary['daily_schedule'] and getattr(self.config, 'upcoming_ai_summary_enabled', True):
            # Brief overview when AI summary is enabled
            daily_counts = {day.split(',')[0]: len(meetings) for day, meetings in summary['daily_schedule'].items()}
            if daily_counts:
                brief_text = "*Daily Overview:* " + " | ".join([f"{day} ({count})" for day, count in list(daily_counts.items())[:5]])
                if len(daily_counts) > 5:
                    brief_text += f" | +{len(daily_counts) - 5} more days"
                
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": brief_text
                    }
                })
        
        # Key meetings
        if summary['key_meetings']:
            key_meetings_text = "*Important Meetings to Watch:*\n"
            for meeting in summary['key_meetings'][:5]:  # Limit to 5 key meetings
                key_meetings_text += f"• {meeting['time']} on {meeting['day']} - {meeting['title']} ({meeting['reason']})\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": key_meetings_text
                }
            })
        
        # Focus opportunities
        if summary['focus_opportunities']:
            focus_text = "*🎯 Focus Time Opportunities:*\n"
            for opportunity in summary['focus_opportunities']:
                focus_text += f"• {opportunity}\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": focus_text
                }
            })
        
        return blocks
    
    def _generate_upcoming_ai_summary(self, upcoming_week_summary: Dict[str, Any]) -> str:
        """Generate an AI-powered summary of the upcoming week schedule."""
        if not self.config.openai_api_key or not self.config.ai_categorization_enabled:
            return self._generate_basic_upcoming_summary(upcoming_week_summary)
        
        try:
            import openai
            logger.info("Generating AI-powered upcoming week summary...")
            
            # Prepare data for AI analysis
            total_events = upcoming_week_summary['total_events']
            daily_schedule = upcoming_week_summary.get('daily_schedule', {})
            key_meetings = upcoming_week_summary.get('key_meetings', [])
            focus_opportunities = upcoming_week_summary.get('focus_opportunities', [])
            
            # Analyze daily distribution
            daily_loads = {}
            busiest_day = ""
            lightest_day = ""
            if daily_schedule:
                for day, meetings in daily_schedule.items():
                    daily_loads[day] = len(meetings)
                
                busiest_day = max(daily_loads.items(), key=lambda x: x[1])[0] if daily_loads else ""
                lightest_day = min(daily_loads.items(), key=lambda x: x[1])[0] if daily_loads else ""
            
            # Get meeting types from titles
            meeting_types = []
            for day, meetings in daily_schedule.items():
                for meeting in meetings[:3]:  # Sample a few meetings
                    meeting_types.append(meeting['title'])
            
            # Build context for AI
            context = f"""Upcoming week schedule analysis:
- Total scheduled meetings: {total_events}
- Busiest day: {busiest_day} ({daily_loads.get(busiest_day, 0)} meetings)
- Lightest day: {lightest_day} ({daily_loads.get(lightest_day, 0)} meetings)
- Key/important meetings: {len(key_meetings)}
- Focus opportunities: {len(focus_opportunities)} days
- Sample meeting titles: {', '.join(meeting_types[:5])}
- Daily breakdown: {', '.join([f"{day.split(',')[0]} ({count})" for day, count in daily_loads.items()])}
"""

            prompt = f"""Write a helpful 3-4 sentence summary of this person's upcoming week schedule. Focus on:
1. Overall workload and meeting density
2. Strategic advice about time management  
3. Highlight the best days for focus work or busiest days to prepare for
4. Note any patterns or important meetings to be aware of

Write in a supportive, coach-like tone. Start with "Looking ahead..."

Schedule data:
{context}"""

            # Handle both old and new OpenAI API versions
            if hasattr(openai, 'OpenAI'):
                # New API (v1.0+)
                client = openai.OpenAI(api_key=self.config.openai_api_key)
                response = client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                summary = response.choices[0].message.content.strip()
            else:
                # Old API (v0.x)
                openai.api_key = self.config.openai_api_key
                response = openai.ChatCompletion.create(
                    model=self.config.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                summary = response.choices[0].message.content.strip()
            
            logger.info("Successfully generated AI-powered upcoming week summary")
            return summary
            
        except ImportError as e:
            logger.warning(f"OpenAI library not available for upcoming summary: {str(e)}")
            return self._generate_basic_upcoming_summary(upcoming_week_summary)
        except Exception as e:
            logger.warning(f"Failed to generate AI upcoming summary: {type(e).__name__}: {str(e)}")
            logger.warning("Falling back to basic upcoming summary")
            return self._generate_basic_upcoming_summary(upcoming_week_summary)
    
    def _generate_basic_upcoming_summary(self, upcoming_week_summary: Dict[str, Any]) -> str:
        """Generate a basic written summary of upcoming week without AI."""
        total_events = upcoming_week_summary['total_events']
        daily_schedule = upcoming_week_summary.get('daily_schedule', {})
        focus_opportunities = upcoming_week_summary.get('focus_opportunities', [])
        
        if total_events == 0:
            return "Looking ahead, you have a completely open week with no scheduled meetings. Perfect time for deep work and catching up on projects!"
        
        # Determine meeting load
        if total_events >= 20:
            load_desc = "a packed week"
        elif total_events >= 10:
            load_desc = "a busy week"
        else:
            load_desc = "a manageable week"
        
        # Find busiest day
        busiest_day = ""
        if daily_schedule:
            busiest_day_data = max(daily_schedule.items(), key=lambda x: len(x[1]))
            busiest_day = f" {busiest_day_data[0].split(',')[0]} looks busiest with {len(busiest_day_data[1])} meetings."
        
        # Focus opportunities
        focus_note = ""
        if focus_opportunities:
            focus_note = f" You have {len(focus_opportunities)} days that look good for focus work."
        
        return f"Looking ahead, you have {load_desc} with {total_events} scheduled meetings.{busiest_day}{focus_note}"
    
    def _generate_written_summary(self, past_week_analysis: Dict[str, Any], 
                                upcoming_week_summary: Dict[str, Any]) -> str:
        """Generate an AI-powered written summary of the week."""
        # Debug logging for configuration
        logger.info(f"AI Summary Debug - API Key present: {bool(self.config.openai_api_key)}")
        logger.info(f"AI Summary Debug - AI enabled: {self.config.ai_categorization_enabled}")
        
        if not self.config.openai_api_key:
            logger.info("Using basic summary: No OpenAI API key configured")
            return self._generate_basic_summary(past_week_analysis, upcoming_week_summary)
        
        if not self.config.ai_categorization_enabled:
            logger.info("Using basic summary: AI categorization disabled")
            return self._generate_basic_summary(past_week_analysis, upcoming_week_summary)
        
        try:
            import openai
            logger.info("Attempting to generate AI-powered summary...")
            
            # Prepare data for AI analysis
            total_events = past_week_analysis['total_events']
            total_time = self._format_duration(past_week_analysis['total_meeting_time'])
            working_hours = self._format_duration(past_week_analysis['working_hours_time'])
            after_hours = self._format_duration(past_week_analysis['after_hours_time'])
            
            # Get top meeting types
            category_breakdown = past_week_analysis.get('category_breakdown', {})
            top_categories = sorted(category_breakdown.items(), 
                                  key=lambda x: x[1]['count'], reverse=True)[:3]
            
            # Get daily distribution
            daily_breakdown = past_week_analysis.get('daily_breakdown', {})
            busiest_day = max(daily_breakdown.items(), 
                            key=lambda x: x[1]['events'])[0] if daily_breakdown else "Unknown"
            
            # Upcoming week info
            upcoming_events = upcoming_week_summary['total_events']
            focus_opportunities = upcoming_week_summary.get('focus_opportunities', [])
            
            # Build context for AI
            context = f"""Past week statistics:
- Total meetings: {total_events}
- Total meeting time: {total_time}
- Working hours meetings: {working_hours}
- After-hours meetings: {after_hours}
- Busiest day: {busiest_day}
- Top meeting types: {', '.join([f"{cat} ({stats['count']})" for cat, stats in top_categories])}

Upcoming week:
- Scheduled meetings: {upcoming_events}
- Focus opportunities: {len(focus_opportunities)} days
"""

            prompt = f"""Write a brief, professional summary of this person's meeting week in 4-5 sentences. Focus on:
1. Overall meeting load and time investment
2. Key meeting patterns or notable trends
3. Work-life balance observations
4. One actionable insight for the upcoming week

Keep it conversational and helpful, like advice from a productivity coach.

Data:
{context}

Write a summary in this style: "This week you had..."
"""

            # Handle both old and new OpenAI API versions
            if hasattr(openai, 'OpenAI'):
                # New API (v1.0+)
                client = openai.OpenAI(api_key=self.config.openai_api_key)
                response = client.chat.completions.create(
                    model=self.config.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                summary = response.choices[0].message.content.strip()
            else:
                # Old API (v0.x)
                openai.api_key = self.config.openai_api_key
                response = openai.ChatCompletion.create(
                    model=self.config.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                summary = response.choices[0].message.content.strip()
            logger.info("Successfully generated AI-powered summary")
            return summary
            
        except ImportError as e:
            logger.warning(f"OpenAI library not available: {str(e)}")
            return self._generate_basic_summary(past_week_analysis, upcoming_week_summary)
        except Exception as e:
            logger.warning(f"Failed to generate AI summary: {type(e).__name__}: {str(e)}")
            logger.warning("Falling back to basic summary")
            return self._generate_basic_summary(past_week_analysis, upcoming_week_summary)
    
    def _generate_basic_summary(self, past_week_analysis: Dict[str, Any], 
                              upcoming_week_summary: Dict[str, Any]) -> str:
        """Generate a basic written summary without AI."""
        total_events = past_week_analysis['total_events']
        total_time = self._format_duration(past_week_analysis['total_meeting_time'])
        upcoming_events = upcoming_week_summary['total_events']
        
        if total_events == 0:
            return "This week was unusually quiet with no scheduled meetings. Great time for deep work! Next week brings some meetings back to your calendar."
        
        # Determine meeting load
        if total_events >= 20:
            load_desc = "a heavy meeting week"
        elif total_events >= 10:
            load_desc = "a moderately busy meeting week"
        else:
            load_desc = "a light meeting week"
        
        # Get top category if available
        category_breakdown = past_week_analysis.get('category_breakdown', {})
        if category_breakdown:
            top_category = max(category_breakdown.items(), key=lambda x: x[1]['count'])
            category_insight = f", with {top_category[0].replace('_', ' ')} meetings being most common"
        else:
            category_insight = ""
        
        return f"This week you had {load_desc} with {total_events} meetings totaling {total_time}{category_insight}. Next week has {upcoming_events} meetings scheduled."
    
    def generate_weekly_report(self, past_week_analysis: Dict[str, Any], 
                             upcoming_week_summary: Dict[str, Any]) -> List[Dict]:
        """Generate the complete weekly report as Slack blocks."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "🗓️ *Weekly Calendar Report* 🗓️\n_Your weekly calendar analysis and upcoming schedule preview_"
                }
            }
        ]
        
        # Add written summary if enabled
        if getattr(self.config, 'written_summary_enabled', True):
            summary = self._generate_written_summary(past_week_analysis, upcoming_week_summary)
            blocks.extend([
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"📝 *Week Summary*\n{summary}"
                    }
                }
            ])
        
        # Add past week analysis
        blocks.extend(self._create_past_week_section(past_week_analysis))
        
        # Add upcoming week summary
        blocks.extend(self._create_upcoming_week_section(upcoming_week_summary))
        
        # Add footer
        blocks.extend([
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "📈 _Report generated by Calendar Analyzer_ | Configure your preferences in the app settings"
                    }
                ]
            }
        ])
        
        return blocks
    
    def send_report(self, blocks: List[Dict]):
        """Send the weekly report to Slack."""
        try:
            # Determine the target (channel or user DM)
            if self.config.slack_user_id:
                # Send as direct message
                channel = self.config.slack_user_id
                logger.info(f"Sending report as DM to user {self.config.slack_user_id}")
            else:
                # Send to channel
                channel = self.config.slack_channel
                logger.info(f"Sending report to channel {self.config.slack_channel}")
            
            response = self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text="Weekly Calendar Report"  # Fallback text for notifications
            )
            
            logger.info(f"Successfully sent report to Slack: {response['ts']}")
            
        except SlackApiError as e:
            logger.error(f"Error sending report to Slack: {e.response['error']}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending report: {str(e)}")
            raise
    
    def send_error_notification(self, error_message: str):
        """Send an error notification to Slack."""
        try:
            blocks = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "🚨 *Calendar Analyzer Error*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"An error occurred while generating your weekly calendar report:\n\n```{error_message}```"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Please check the application logs for more details."
                    }
                }
            ]
            
            # Send to the same target as regular reports
            channel = self.config.slack_user_id if self.config.slack_user_id else self.config.slack_channel
            
            self.client.chat_postMessage(
                channel=channel,
                blocks=blocks,
                text="Calendar Analyzer Error"
            )
            
            logger.info("Error notification sent to Slack")
            
        except Exception as e:
            logger.error(f"Failed to send error notification to Slack: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test the Slack connection and permissions."""
        try:
            response = self.client.auth_test()
            logger.info(f"Slack connection test successful. Bot: {response['user']}")
            return True
        except SlackApiError as e:
            logger.error(f"Slack connection test failed: {e.response['error']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error testing Slack connection: {str(e)}")
            return False 