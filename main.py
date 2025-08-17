#!/usr/bin/env python3
"""
Calendar Slack Analyzer - Main Application
Analyzes Google Calendar data and sends weekly reports to Slack
"""

import os
import schedule
import time
import logging
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

from calendar_analyzer import CalendarAnalyzer
from slack_reporter import SlackReporter
from config import Config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('calendar_analyzer.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_weekly_analysis():
    """Run the weekly calendar analysis and send Slack report."""
    try:
        logger.info("Starting weekly calendar analysis...")
        
        # Initialize components
        config = Config()
        calendar_analyzer = CalendarAnalyzer(config)
        slack_reporter = SlackReporter(config)
        
        # Get date ranges for analysis
        today = datetime.now().date()
        
        # Past week: Last Monday to Sunday
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        # Upcoming week: This Monday to Sunday
        this_monday = today - timedelta(days=days_since_monday)
        this_sunday = this_monday + timedelta(days=6)
        
        logger.info(f"Analyzing past week: {last_monday} to {last_sunday}")
        logger.info(f"Summarizing upcoming week: {this_monday} to {this_sunday}")
        
        # Analyze past week
        past_week_events = calendar_analyzer.get_events(last_monday, last_sunday)
        past_week_analysis = calendar_analyzer.analyze_week(past_week_events, last_monday, last_sunday)
        
        # Get upcoming week events
        upcoming_week_events = calendar_analyzer.get_events(this_monday, this_sunday)
        upcoming_week_summary = calendar_analyzer.summarize_upcoming_week(upcoming_week_events, this_monday, this_sunday)
        
        # Generate and send report
        report = slack_reporter.generate_weekly_report(past_week_analysis, upcoming_week_summary)
        slack_reporter.send_report(report)
        
        logger.info("Weekly analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during weekly analysis: {str(e)}")
        # Send error notification to Slack
        try:
            slack_reporter = SlackReporter(Config())
            slack_reporter.send_error_notification(str(e))
        except:
            pass

def run_weekly_analysis_test_mode():
    """Run the weekly calendar analysis in test mode (don't send to Slack)."""
    try:
        logger.info("Starting weekly calendar analysis (TEST MODE)...")
        
        # Initialize components
        config = Config()
        calendar_analyzer = CalendarAnalyzer(config)
        slack_reporter = SlackReporter(config)
        
        # Get date ranges for analysis
        today = datetime.now().date()
        
        # Past week: Last Monday to Sunday
        days_since_monday = today.weekday()
        last_monday = today - timedelta(days=days_since_monday + 7)
        last_sunday = last_monday + timedelta(days=6)
        
        # Upcoming week: This Monday to Sunday
        this_monday = today - timedelta(days=days_since_monday)
        this_sunday = this_monday + timedelta(days=6)
        
        logger.info(f"Analyzing past week: {last_monday} to {last_sunday}")
        logger.info(f"Summarizing upcoming week: {this_monday} to {this_sunday}")
        
        # Analyze past week
        past_week_events = calendar_analyzer.get_events(last_monday, last_sunday)
        past_week_analysis = calendar_analyzer.analyze_week(past_week_events, last_monday, last_sunday)
        
        # Get upcoming week events
        upcoming_week_events = calendar_analyzer.get_events(this_monday, this_sunday)
        upcoming_week_summary = calendar_analyzer.summarize_upcoming_week(upcoming_week_events, this_monday, this_sunday)
        
        # Generate report (but don't send)
        report = slack_reporter.generate_weekly_report(past_week_analysis, upcoming_week_summary)
        
        # Print analysis results instead of sending to Slack
        print("\n" + "="*60)
        print("📊 CALENDAR ANALYSIS RESULTS (TEST MODE)")
        print("="*60)
        
        # Generate and display written summary
        if config.written_summary_enabled:
            summary = slack_reporter._generate_written_summary(past_week_analysis, upcoming_week_summary)
            print(f"\n📝 Written Summary:")
            print(f"   {summary}")
        
        print(f"\n📅 Past Week ({past_week_analysis['period']}):")
        print(f"  • Total meetings: {past_week_analysis['total_events']}")
        if past_week_analysis['total_events'] > 0:
            total_time = past_week_analysis['total_meeting_time']
            print(f"  • Total meeting time: {total_time}")
            print(f"  • Working hours: {past_week_analysis['working_hours_time']}")
            print(f"  • After hours: {past_week_analysis['after_hours_time']}")
            
            if past_week_analysis['insights']:
                print("  • Key insights:")
                for insight in past_week_analysis['insights']:
                    print(f"    - {insight}")
        
        print(f"\n🗓️ Upcoming Week ({upcoming_week_summary['period']}):")
        print(f"  • Scheduled meetings: {upcoming_week_summary['total_events']}")
        if upcoming_week_summary['focus_opportunities']:
            print("  • Focus opportunities:")
            for opp in upcoming_week_summary['focus_opportunities']:
                print(f"    - {opp}")
        
        print(f"\n📝 Report generated with {len(report)} Slack blocks")
        print("   (In normal mode, this would be sent to Slack)")
        
        logger.info("Test mode analysis completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during test mode analysis: {str(e)}")
        raise

def main():
    """Main application entry point."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Calendar Slack Analyzer')
    parser.add_argument('--run-now', '--immediate', action='store_true',
                       help='Run the analysis immediately and exit (skip scheduling)')
    parser.add_argument('--test-only', action='store_true',
                       help='Run analysis but don\'t send to Slack (for testing)')
    args = parser.parse_args()
    
    logger.info("Calendar Slack Analyzer starting up...")
    
    # Verify configuration
    config = Config()
    if not config.validate():
        logger.error("Configuration validation failed. Please check your environment variables.")
        return
    
    # If immediate run requested
    if args.run_now or os.getenv('RUN_IMMEDIATELY', 'false').lower() == 'true':
        logger.info("Running analysis immediately...")
        try:
            if args.test_only:
                logger.info("TEST MODE: Analysis will run but report won't be sent to Slack")
                run_weekly_analysis_test_mode()
            else:
                run_weekly_analysis()
            logger.info("Immediate analysis completed!")
        except Exception as e:
            logger.error(f"Error during immediate analysis: {str(e)}")
        return
    
    # Normal scheduled operation
    # Schedule weekly analysis for Monday mornings at 9:00 AM
    schedule.every().monday.at("09:00").do(run_weekly_analysis)
    
    logger.info("Scheduled weekly analysis for Mondays at 9:00 AM")
    logger.info("Calendar Analyzer is running. Press Ctrl+C to stop.")
    logger.info("Tip: Use 'python main.py --run-now' to run immediately")
    
    # Keep the application running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Calendar Analyzer shutting down...")

if __name__ == "__main__":
    main() 