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
        
        # Daily schedule (show first few days)
        if summary['daily_schedule']:
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