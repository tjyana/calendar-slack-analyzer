#!/usr/bin/env python3
"""
Setup script for Calendar Slack Analyzer
Helps users configure their environment
"""

import os
import sys

ENV_TEMPLATE = """# Google Calendar API Configuration
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json
GOOGLE_CALENDAR_ID=primary

# Slack Configuration (Required)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_CHANNEL=#general
# Optional: Send as DM instead of to channel
# SLACK_USER_ID=U1234567890

# Analysis Settings
TIMEZONE=Asia/Tokyo
WORKING_HOURS_START=9
WORKING_HOURS_END=17
EXCLUDE_WEEKENDS=true

# Report Settings
INCLUDE_PRIVATE_EVENTS=false
MAX_UPCOMING_EVENTS=10

# Testing (set to true to run analysis immediately on startup)
RUN_IMMEDIATELY=false
"""

def create_env_file():
    """Create the .env file from template."""
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").lower()
        if response != 'y':
            print("Keeping existing .env file.")
            return False
    
    with open('.env', 'w') as f:
        f.write(ENV_TEMPLATE)
    
    print("✅ Created .env file with default settings")
    return True

def prompt_for_slack_token():
    """Prompt user to enter their Slack bot token."""
    print("\n🤖 Slack Bot Setup")
    print("=" * 30)
    print("You need to create a Slack bot and get a bot token.")
    print("1. Go to https://api.slack.com/apps")
    print("2. Create a new app for your workspace")
    print("3. Add bot token scopes: chat:write, chat:write.public")
    print("4. Install the app to your workspace")
    print("5. Copy the Bot User OAuth Token (starts with xoxb-)")
    
    token = input("\nEnter your Slack bot token (or press Enter to skip): ").strip()
    if token:
        # Update the .env file
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('SLACK_BOT_TOKEN=xoxb-your-bot-token-here', f'SLACK_BOT_TOKEN={token}')
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ Updated .env file with your Slack token")
            return True
        except Exception as e:
            print(f"❌ Error updating .env file: {e}")
            return False
    else:
        print("⏭️  Skipped Slack token setup. You can edit .env manually later.")
        return False

def prompt_for_channel():
    """Prompt user to enter their preferred Slack channel."""
    print("\n📢 Slack Channel Setup")
    print("=" * 30)
    channel = input("Enter the Slack channel for reports (default: #general): ").strip()
    
    if channel:
        if not channel.startswith('#'):
            channel = '#' + channel
        
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('SLACK_CHANNEL=#general', f'SLACK_CHANNEL={channel}')
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print(f"✅ Updated channel to {channel}")
            return True
        except Exception as e:
            print(f"❌ Error updating channel: {e}")
            return False
    else:
        print("⏭️  Using default channel: #general")
        return True

def prompt_for_timezone():
    """Prompt user to enter their timezone."""
    print("\n🌍 Timezone Setup")
    print("=" * 30)
    print("Examples: Asia/Tokyo, America/New_York, Europe/London, UTC")
    timezone = input("Enter your timezone (default: Asia/Tokyo): ").strip()
    
    if timezone:
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            content = content.replace('TIMEZONE=Asia/Tokyo', f'TIMEZONE={timezone}')
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print(f"✅ Updated timezone to {timezone}")
            return True
        except Exception as e:
            print(f"❌ Error updating timezone: {e}")
            return False
    else:
        print("⏭️  Using default timezone: Asia/Tokyo")
        return True

def check_credentials():
    """Check if Google credentials file exists."""
    print("\n📅 Google Calendar Setup")
    print("=" * 30)
    
    if os.path.exists('credentials.json'):
        print("✅ Found credentials.json file")
        return True
    else:
        print("❌ credentials.json not found")
        print("📋 To set up Google Calendar API:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create/select a project")
        print("3. Enable Google Calendar API")
        print("4. Create OAuth 2.0 credentials (Desktop application)")
        print("5. Download and save as 'credentials.json'")
        return False

def main():
    """Run the setup process."""
    print("🚀 Calendar Slack Analyzer - Setup")
    print("=" * 40)
    print("This script will help you configure the application.\n")
    
    # Create .env file
    if create_env_file():
        print("📝 Now let's configure your settings...\n")
        
        # Configure Slack
        prompt_for_slack_token()
        prompt_for_channel()
        
        # Configure timezone
        prompt_for_timezone()
    
    # Check Google credentials
    check_credentials()
    
    # Final instructions
    print("\n" + "=" * 40)
    print("📋 NEXT STEPS")
    print("=" * 40)
    print("1. ✅ Environment file created (.env)")
    print("2. 📝 Edit .env if you need to change any settings")
    
    if not os.path.exists('credentials.json'):
        print("3. ⚠️  Download credentials.json from Google Cloud Console")
        print("4. 🧪 Run setup test: python test_setup.py")
        print("5. 🚀 Start the app: python main.py")
    else:
        print("3. ✅ Google credentials found")
        print("4. 🧪 Run setup test: python test_setup.py")
        print("5. 🚀 Start the app: python main.py")
    
    print("\n💡 Quick commands:")
    print("   Demo output: python demo.py")
    print("   Test run: python main.py --run-now --test-only")
    print("   Live run: python main.py --run-now")
    print("📖 For detailed instructions: see README.md")

if __name__ == "__main__":
    main() 