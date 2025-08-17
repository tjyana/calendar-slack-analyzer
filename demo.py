#!/usr/bin/env python3
"""
Demo script for Calendar Slack Analyzer
Shows sample output without requiring real calendar/Slack connections
"""

from datetime import datetime, timedelta

def main():
    """Run the demo."""
    print("🚀 Calendar Slack Analyzer - Demo")
    print("This shows sample output that the app would generate.\n")
    
    print("📊 PAST WEEK ANALYSIS")
    print("=" * 50)
    print("Period: 2024-01-08 to 2024-01-14")
    
    print("\n📝 AI WEEK SUMMARY:")
    print("This week you had a heavy meeting schedule with 18 meetings totaling 12h 30m, dominated by")
    print("daily standups and planning sessions. While most meetings stayed within working hours, you")
    print("spent 18% of meeting time after hours. Consider blocking focus time next week, especially")
    print("on Thursday which looks lighter with only 2 scheduled meetings.")
    
    print("\n📊 DETAILED BREAKDOWN:")
    print("Total Meetings: 18")
    print("Total Meeting Time: 12h 30m")
    print("Working Hours: 10h 15m")
    print("After Hours: 2h 15m")
    
    print("\nDaily Breakdown:")
    print("  • Monday: 4 meetings (2h 30m)")
    print("  • Tuesday: 3 meetings (2h 0m)")
    print("  • Wednesday: 5 meetings (3h 15m)")
    print("  • Thursday: 3 meetings (2h 30m)")
    print("  • Friday: 3 meetings (2h 15m)")
    
    print("\nMeeting Types (AI-Categorized):")
    print("  • Standup: 5 meetings (2h 30m)")
    print("  • Planning: 3 meetings (3h 0m)")
    print("  • Review: 3 meetings (2h 30m)")
    print("  • One On One: 2 meetings (1h 0m)")
    print("  • Client: 2 meetings (1h 30m)")
    print("  • Technical: 2 meetings (2h 0m)")
    print("  • Training: 1 meeting (1h 0m)")
    
    print("\nKey Insights:")
    print("  • 📅 Heavy meeting week - consider blocking focus time")
    print("  • ⏰ 18.0% of meetings were outside working hours")
    print("  • 🎯 Most common meeting type: standup (5 meetings)")
    print("  • 📊 Busiest day: Wednesday with 5 meetings")
    
    print("\n📅 UPCOMING WEEK PREVIEW")
    print("=" * 50)
    print("Period: 2024-01-15 to 2024-01-21")
    print("Total Scheduled Meetings: 15")
    
    print("\nThis Week's Schedule:")
    print("\n  Monday, January 15 (3 meetings):")
    print("    • 09:00 - Weekly Planning (1:00:00)")
    print("    • 14:00 - Product Review (1:30:00)")
    print("    • 16:00 - 1:1 with Manager (0:30:00)")
    
    print("\n  Tuesday, January 16 (2 meetings):")
    print("    • 09:30 - Daily Standup (0:15:00)")
    print("    • 11:00 - Client Presentation (2:00:00)")
    
    print("\nImportant Meetings to Watch:")
    print("  • 11:00 on Tuesday, January 16 - Client Presentation (Long duration)")
    print("  • 14:00 on Friday, January 19 - Demo Day (Many attendees)")
    
    print("\n🎯 Focus Time Opportunities:")
    print("  • Thursday, January 18 - Good for focus work (2 meetings)")
    
    print("\n💬 SLACK MESSAGE PREVIEW")
    print("=" * 50)
    print("🗓️ *Weekly Calendar Report* 🗓️")
    print("_Your weekly calendar analysis and upcoming schedule preview_")
    print()
    print("📝 *Week Summary*")
    print("This week you had a heavy meeting schedule with 18 meetings totaling 12h 30m,")
    print("dominated by daily standups and planning sessions. Consider blocking focus")
    print("time next week, especially on Thursday which looks lighter.")
    print()
    print("📊 *Past Week Analysis*")
    print("*Total Meetings:* 18 | *Meeting Time:* 12h 30m")
    print("*Top Categories:* Standup (5), Planning (3), Review (3)")
    print()
    print("📅 *Upcoming Week Preview*")
    print("*Total Scheduled:* 15 meetings")
    print("*Focus Opportunity:* Thursday - Good for deep work (2 meetings)")
    
    print("\n" + "=" * 50)
    print("📝 NEXT STEPS")
    print("=" * 50)
    print("1. Set up Google Calendar API credentials (credentials.json)")
    print("2. Create a Slack bot and get the bot token")
    print("3. Copy .env.example to .env and configure")
    print("4. Run setup test: python test_setup.py")
    print("5. Start the analyzer: python main.py")
    print("\nFor detailed setup instructions, see README.md")

if __name__ == "__main__":
    main() 