# Calendar Slack Analyzer 📅

A Python application that analyzes your Google Calendar data and sends weekly reports to Slack. Get insights into your meeting patterns, time usage, and upcoming schedule every Monday morning.

## Features 🚀

### Past Week Analysis
- **AI-Written Summary**: Narrative overview of your week with actionable insights
- **Meeting Patterns**: Categorizes meetings (standups, reviews, planning, 1:1s, etc.)
- **Time Usage**: Tracks total meeting time, working hours vs after-hours
- **Daily Breakdown**: Shows meeting distribution across the week
- **Smart Insights**: Provides actionable insights about your meeting habits
- **Focused Analysis**: Excludes all-day events by default (configurable)

### Upcoming Week Preview
- **Schedule Overview**: Summary of upcoming meetings
- **Key Meetings**: Highlights important/long meetings
- **Focus Opportunities**: Identifies days with lighter meeting loads
- **Time Awareness**: Helps you prepare for busy periods

### AI-Powered Meeting Categorization
The app uses AI to intelligently categorize meetings based on context:
- **Standup**: Daily team check-ins, status updates, sync meetings
- **Planning**: Sprint planning, project planning, roadmap sessions
- **Review**: Code reviews, retrospectives, demos, performance reviews
- **One-on-One**: 1:1 meetings, personal check-ins, manager meetings
- **Interview**: Job interviews, candidate meetings, hiring discussions
- **Training**: Learning sessions, workshops, onboarding
- **Brainstorm**: Ideation sessions, creative meetings, problem-solving
- **Client**: External client meetings, customer calls, vendor meetings
- **Social**: Team building, social events, casual gatherings
- **Administrative**: Budget meetings, compliance, reporting
- **Technical**: Technical deep dives, architecture discussions
- **Other**: Anything that doesn't fit the above categories

*Falls back to keyword matching if AI is unavailable*

## Setup Instructions 🛠️

### 1. Install Dependencies

```bash
cd calendar-slack-analyzer
pip install -r requirements.txt
```

### 2. Google Calendar API Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API
4. Create credentials (OAuth 2.0 Client ID) for a desktop application
5. Download the credentials file and save it as `credentials.json` in the project directory

### 3. Slack Bot Setup

1. Go to [Slack API](https://api.slack.com/apps)
2. Create a new app for your workspace
3. Add the following bot token scopes:
   - `chat:write`
   - `chat:write.public`
   - `im:write` (if sending DMs)
4. Install the app to your workspace
5. Copy the Bot User OAuth Token (starts with `xoxb-`)

### 4. OpenAI API Setup (Optional but Recommended)

1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Copy the API key (starts with `sk-`)

*Note: AI categorization provides much more accurate meeting classification than keyword matching. The AI also generates personalized written summaries of your week with actionable insights. Without OpenAI, the app falls back to basic keyword detection and simple summaries.*

### 5. Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```env
   # Required
   SLACK_BOT_TOKEN=xoxb-your-actual-bot-token-here
   
   # Optional customizations
   SLACK_CHANNEL=#your-channel
   TIMEZONE=Asia/Tokyo
   WORKING_HOURS_START=9
   WORKING_HOURS_END=17
   ```

### 5. First Run & Authentication

```bash
python main.py
```

On first run, the app will:
1. Open a browser for Google Calendar authentication
2. Save your authentication token for future use
3. Test the Slack connection
4. Start the scheduler

## Usage 📊

### Automatic Operation
- The app runs continuously and sends reports every Monday at 9:00 AM
- Reports include analysis of the previous week and preview of the upcoming week

### Manual Testing

**Immediate Run (Recommended):**
```bash
# Run analysis immediately and send to Slack
python main.py --run-now

# Run analysis immediately but only show results (don't send to Slack)
python main.py --run-now --test-only
```

**Alternative methods:**
```bash
# Set RUN_IMMEDIATELY=true in .env, then:
python main.py

# Or use the shorter alias:
python main.py --immediate
```

### Report Content
Each weekly report includes:

**Past Week Analysis:**
- AI-generated narrative summary with actionable insights
- Total meetings and time spent
- Daily breakdown of meetings
- Meeting type categorization
- Working hours vs after-hours analysis
- Key insights and patterns

**Upcoming Week Preview:**
- Schedule overview by day
- Important meetings to watch
- Focus time opportunities
- Preparation insights

## Configuration Options ⚙️

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CREDENTIALS_PATH` | `credentials.json` | Path to Google credentials file |
| `GOOGLE_CALENDAR_ID` | `primary` | Calendar to analyze |
| `SLACK_BOT_TOKEN` | - | **Required** Slack bot token |
| `SLACK_CHANNEL` | `#general` | Channel for reports |
| `SLACK_USER_ID` | - | Send DM instead of channel |
| `OPENAI_API_KEY` | - | OpenAI API key for AI categorization |
| `AI_CATEGORIZATION_ENABLED` | `true` | Enable AI-powered meeting categorization |
| `OPENAI_MODEL` | `gpt-3.5-turbo` | OpenAI model to use |
| `TIMEZONE` | `UTC` | Your timezone |
| `WORKING_HOURS_START` | `9` | Work day start hour |
| `WORKING_HOURS_END` | `17` | Work day end hour |
| `INCLUDE_PRIVATE_EVENTS` | `false` | Include private calendar events |
| `INCLUDE_ALL_DAY_EVENTS` | `false` | Include all-day events in analysis |
| `WRITTEN_SUMMARY_ENABLED` | `true` | Enable AI-generated written summaries |
| `MAX_UPCOMING_EVENTS` | `10` | Max events in upcoming preview |

## Troubleshooting 🔧

### Common Issues

**Google Calendar Authentication Fails:**
- Ensure `credentials.json` is in the project directory
- Check that Google Calendar API is enabled in Google Cloud Console
- Delete `token.json` and re-authenticate if needed

**Slack Reports Not Sending:**
- Verify the bot token is correct
- Ensure the bot is added to the target channel
- Check bot permissions include `chat:write`

**No Events Found:**
- Verify the calendar ID (use `primary` for your main calendar)
- Check timezone settings match your calendar
- Ensure the date range includes actual events

### Logs
Check `calendar_analyzer.log` for detailed error information.

### Testing Slack Connection
```python
from config import Config
from slack_reporter import SlackReporter

config = Config()
reporter = SlackReporter(config)
print("Slack connection:", reporter.test_connection())
```

### Testing AI Configuration
If AI summaries aren't working, run the dedicated AI test:
```bash
python test_ai.py
```
This will check your OpenAI configuration and test summary generation.

## Running in Production 🏭

### As a Service (Linux)
1. Create a systemd service file
2. Set up log rotation
3. Configure automatic restarts

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

### Environment Considerations
- Ensure persistent storage for `token.json`
- Set up proper logging and monitoring
- Consider using secrets management for tokens

## Contributing 🤝

Feel free to submit issues and enhancement requests!

## License 📄

This project is licensed under the MIT License. 