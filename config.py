"""
Configuration management for Calendar Slack Analyzer
"""

import os
from typing import Optional

class Config:
    """Configuration class for managing app settings."""
    
    def __init__(self):
        # Google Calendar API settings
        self.google_credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
        self.google_token_path = os.getenv('GOOGLE_TOKEN_PATH', 'token.json')
        self.calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        # Slack settings
        self.slack_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_channel = os.getenv('SLACK_CHANNEL', '#general')
        self.slack_user_id = os.getenv('SLACK_USER_ID')  # Optional: for direct messages
        
        # Analysis settings
        self.timezone = os.getenv('TIMEZONE', 'UTC')
        self.working_hours_start = int(os.getenv('WORKING_HOURS_START', '9'))
        self.working_hours_end = int(os.getenv('WORKING_HOURS_END', '17'))
        self.exclude_weekends = os.getenv('EXCLUDE_WEEKENDS', 'true').lower() == 'true'
        
        # Meeting categories for pattern analysis
        self.meeting_keywords = {
            'standup': ['standup', 'daily', 'scrum'],
            'review': ['review', 'retrospective', 'demo'],
            'planning': ['planning', 'grooming', 'estimation'],
            'one_on_one': ['1:1', 'one on one', 'one-on-one', '1-1'],
            'interview': ['interview', 'hiring', 'candidate'],
            'external': ['client', 'customer', 'vendor', 'external']
        }
        
        # Report settings
        self.include_private_events = os.getenv('INCLUDE_PRIVATE_EVENTS', 'false').lower() == 'true'
        self.max_upcoming_events = int(os.getenv('MAX_UPCOMING_EVENTS', '10'))
    
    def validate(self) -> bool:
        """Validate that all required configuration is present."""
        required_vars = [
            ('SLACK_BOT_TOKEN', self.slack_token),
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        return True
    
    def get_scopes(self) -> list:
        """Get the required Google Calendar API scopes."""
        return ['https://www.googleapis.com/auth/calendar.readonly'] 