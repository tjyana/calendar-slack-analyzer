#!/usr/bin/env python3
"""
Setup test script for Calendar Slack Analyzer
Verifies configuration and connections before running the main app
"""

import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

def test_environment():
    """Test that environment variables are properly configured."""
    print("🔧 Testing environment configuration...")
    
    load_dotenv()
    
    # Required variables
    required_vars = {
        'SLACK_BOT_TOKEN': os.getenv('SLACK_BOT_TOKEN'),
    }
    
    # Optional but recommended variables  
    optional_vars = {
        'GOOGLE_CREDENTIALS_PATH': os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json'),
        'SLACK_CHANNEL': os.getenv('SLACK_CHANNEL', '#general'),
        'TIMEZONE': os.getenv('TIMEZONE', 'UTC'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'AI_CATEGORIZATION_ENABLED': os.getenv('AI_CATEGORIZATION_ENABLED', 'true'),
    }
    
    print("Required variables:")
    all_good = True
    for var, value in required_vars.items():
        status = "✅" if value else "❌ MISSING"
        print(f"  {var}: {status}")
        if not value:
            all_good = False
    
    print("\nOptional variables:")
    for var, value in optional_vars.items():
        print(f"  {var}: {value}")
    
    return all_good

def test_google_credentials():
    """Test Google Calendar credentials file."""
    print("\n📅 Testing Google Calendar setup...")
    
    creds_path = os.getenv('GOOGLE_CREDENTIALS_PATH', 'credentials.json')
    
    if os.path.exists(creds_path):
        print(f"✅ Credentials file found: {creds_path}")
        return True
    else:
        print(f"❌ Credentials file not found: {creds_path}")
        print("   Please download credentials.json from Google Cloud Console")
        return False

def test_slack_connection():
    """Test Slack bot connection."""
    print("\n💬 Testing Slack connection...")
    
    try:
        from config import Config
        from slack_reporter import SlackReporter
        
        config = Config()
        reporter = SlackReporter(config)
        
        if reporter.test_connection():
            print("✅ Slack connection successful!")
            return True
        else:
            print("❌ Slack connection failed")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Slack connection error: {e}")
        return False

def test_calendar_connection():
    """Test Google Calendar connection."""
    print("\n📊 Testing Google Calendar connection...")
    
    try:
        from config import Config
        from calendar_analyzer import CalendarAnalyzer
        
        config = Config()
        analyzer = CalendarAnalyzer(config)
        
        # Test with a small date range
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        
        events = analyzer.get_events(yesterday, today)
        print(f"✅ Google Calendar connection successful!")
        print(f"   Found {len(events)} events in the past day")
        return True
        
    except FileNotFoundError as e:
        print(f"❌ Credentials file error: {e}")
        return False
    except Exception as e:
        print(f"❌ Google Calendar connection error: {e}")
        print("   You may need to complete the OAuth flow when running the main app")
        return False

def test_ai_configuration():
    """Test AI configuration for categorization and summaries."""
    print("\n🤖 Testing AI configuration...")
    
    api_key = os.getenv('OPENAI_API_KEY')
    ai_enabled = os.getenv('AI_CATEGORIZATION_ENABLED', 'true').lower() == 'true'
    
    if not api_key:
        print("⚠️  OpenAI API key not configured")
        print("   AI features will fall back to basic keyword matching")
        print("   To enable AI: Add OPENAI_API_KEY to your .env file")
        return True  # Not a failure, just a limitation
    
    if not ai_enabled:
        print("ℹ️  AI categorization disabled")
        print("   Set AI_CATEGORIZATION_ENABLED=true to enable")
        return True
    
    try:
        import openai
        print(f"✅ OpenAI library available")
        
        # Quick API test - handle both old and new OpenAI API versions
        if hasattr(openai, 'OpenAI'):
            # New API (v1.0+)
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
        else:
            # Old API (v0.x)
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
        print("✅ OpenAI API connection successful!")
        print("   AI categorization and summaries will be enabled")
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        print("   Check your API key and billing status")
        return False

def test_dependencies():
    """Test that all required dependencies are installed."""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'google-api-python-client',
        'google-auth-httplib2', 
        'google-auth-oauthlib',
        'slack-sdk',
        'python-dotenv',
        'pandas',
        'numpy',
        'python-dateutil',
        'schedule',
        'pytz',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    else:
        print("✅ All dependencies installed!")
        return True

def main():
    """Run all setup tests."""
    print("🚀 Calendar Slack Analyzer - Setup Test\n")
    
    tests = [
        ("Dependencies", test_dependencies),
        ("Environment", test_environment),
        ("Google Credentials", test_google_credentials),
        ("Slack Connection", test_slack_connection),
        ("Calendar Connection", test_calendar_connection),
        ("AI Configuration", test_ai_configuration),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except KeyboardInterrupt:
            print("\n⏹️  Test interrupted by user")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Unexpected error in {test_name}: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("🎉 All tests passed! You're ready to run the Calendar Analyzer.")
        print("\nTo test immediately:")
        print("  python main.py --run-now --test-only  (test without sending to Slack)")
        print("  python main.py --run-now             (run and send to Slack)")
        print("\nTo start scheduled mode:")
        print("  python main.py                       (runs every Monday at 9:00 AM)")
    else:
        print("❌ Some tests failed. Please fix the issues above before running the app.")
        print("\nFor help, check the README.md file or the troubleshooting section.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 