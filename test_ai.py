#!/usr/bin/env python3
"""
Test script for AI functionality in Calendar Slack Analyzer
Helps diagnose OpenAI configuration issues
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

def test_openai_config():
    """Test OpenAI configuration and connectivity."""
    print("🤖 Testing OpenAI Configuration")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check environment variables
    api_key = os.getenv('OPENAI_API_KEY')
    ai_enabled = os.getenv('AI_CATEGORIZATION_ENABLED', 'true').lower() == 'true'
    model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    print(f"✓ OPENAI_API_KEY: {'✅ Set' if api_key else '❌ Not set'}")
    print(f"✓ AI_CATEGORIZATION_ENABLED: {'✅ True' if ai_enabled else '❌ False'}")
    print(f"✓ OPENAI_MODEL: {model}")
    
    # Check OpenAI library version
    try:
        import openai
        if hasattr(openai, '__version__'):
            version = openai.__version__
            print(f"✓ OpenAI Library Version: {version}")
            if version.startswith('0.'):
                print("  ℹ️  Using older OpenAI API (v0.x) - consider upgrading to v1.x")
            else:
                print("  ✅ Using modern OpenAI API (v1.x+)")
        else:
            print("✓ OpenAI Library Version: Unknown (older version)")
    except ImportError:
        pass
    
    if not api_key:
        print("\n❌ PROBLEM: No OpenAI API key found!")
        print("   Add OPENAI_API_KEY=your-key-here to your .env file")
        print("   Get a key from: https://platform.openai.com/api-keys")
        return False
    
    if not ai_enabled:
        print("\n❌ PROBLEM: AI categorization is disabled!")
        print("   Set AI_CATEGORIZATION_ENABLED=true in your .env file")
        return False
    
    # Test OpenAI library import
    try:
        import openai
        print("✓ OpenAI library: ✅ Available")
    except ImportError:
        print("✓ OpenAI library: ❌ Not installed")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Test API connectivity
    try:
        print("\n🔗 Testing API connectivity...")
        
        # Handle both old and new OpenAI API versions
        if hasattr(openai, 'OpenAI'):
            # New API (v1.0+)
            print("Using OpenAI API v1.0+")
            client = openai.OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'API test successful' in exactly those words."}],
                max_tokens=10,
                temperature=0
            )
            result = response.choices[0].message.content.strip()
        else:
            # Old API (v0.x)
            print("Using OpenAI API v0.x")
            openai.api_key = api_key
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": "Say 'API test successful' in exactly those words."}],
                max_tokens=10,
                temperature=0
            )
            result = response.choices[0].message.content.strip()
        
        if "API test successful" in result:
            print("✅ API Test: Connection successful!")
        else:
            print(f"⚠️  API Test: Unexpected response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ API Test Failed: {type(e).__name__}: {str(e)}")
        
        if "Incorrect API key" in str(e):
            print("   → Check your API key is correct")
        elif "quota" in str(e).lower():
            print("   → Check your OpenAI billing/quota")
        elif "model" in str(e).lower():
            print(f"   → Model '{model}' may not be available")
        
        return False

def test_summary_generation():
    """Test the actual summary generation with sample data."""
    print("\n📝 Testing Summary Generation")
    print("=" * 40)
    
    try:
        from config import Config
        from slack_reporter import SlackReporter
        
        config = Config()
        reporter = SlackReporter(config)
        
        # Create sample data with actual timedelta objects
        sample_analysis = {
            'total_events': 15,
            'total_meeting_time': timedelta(hours=8, minutes=30),
            'working_hours_time': timedelta(hours=7),
            'after_hours_time': timedelta(hours=1, minutes=30),
            'category_breakdown': {
                'standup': {'count': 5, 'total_time': timedelta(hours=2)},
                'planning': {'count': 3, 'total_time': timedelta(hours=2, minutes=30)},
                'one_on_one': {'count': 2, 'total_time': timedelta(hours=1)}
            },
            'daily_breakdown': {
                'Monday': {'events': 3},
                'Tuesday': {'events': 4},
                'Wednesday': {'events': 5},
                'Thursday': {'events': 2},
                'Friday': {'events': 1}
            }
        }
        
        sample_upcoming = {
            'total_events': 12,
            'focus_opportunities': ['Thursday - Good for focus work (2 meetings)']
        }
        
        print("Generating test summary...")
        print("Sample data prepared with:")
        print(f"  - {sample_analysis['total_events']} total events")
        print(f"  - {sample_analysis['total_meeting_time']} total meeting time")
        print("  - Category breakdown with actual counts")
        
        # This will show debug logs and tell us exactly what's happening
        summary = reporter._generate_written_summary(sample_analysis, sample_upcoming)
        
        print(f"\n📋 Generated Summary:")
        print(f"   {summary}")
        
        # Analyze the summary to give feedback
        if "This week you had" in summary:
            print("✅ Summary looks like AI-generated content!")
        elif len(summary) > 100:
            print("✅ Summary is detailed (likely AI-generated)")
        elif len(summary) < 50:
            print("⚠️  Summary is very short (likely basic fallback)")
        else:
            print("ℹ️  Summary generated successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Summary generation failed: {type(e).__name__}: {str(e)}")
        return False

def main():
    """Run all tests."""
    print("🚀 Calendar Analyzer - AI Testing Tool\n")
    
    config_ok = test_openai_config()
    
    if config_ok:
        test_summary_generation()
    
    print("\n" + "=" * 40)
    print("📋 RECOMMENDATIONS")
    print("=" * 40)
    
    if not config_ok:
        print("1. Fix the OpenAI configuration issues above")
        print("2. If using old OpenAI library, consider upgrading:")
        print("   pip install --upgrade openai")
        print("3. Re-run this test: python test_ai.py")
        print("4. Then test the full app: python main.py --run-now --test-only")
    else:
        print("✅ Configuration looks good!")
        print("If you're still seeing basic summaries, check the logs when running:")
        print("   python main.py --run-now --test-only")
        print("Look for 'AI Summary Debug' messages in the output.")
        print("\n💡 For best performance, consider upgrading to OpenAI v1.x:")
        print("   pip install --upgrade openai")

if __name__ == "__main__":
    main() 