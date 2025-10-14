# TruthSocial RSS Scraper & Analyzer

A Python bot that automatically monitors new posts from Donald Trump's TruthSocial account using the RSS feed from [trumpstruth.org](https://trumpstruth.org/feed) and analyzes them for market impact using OpenAI.

## 🎯 Features

### RSS Scraper
- ✅ **RSS-based**: Uses the official RSS feed - no authentication required
- ✅ **Real posts**: Gets actual posts from @realDonaldTrump (not ads)
- ✅ **Automatic deduplication**: Tracks seen posts using real TruthSocial post IDs
- ✅ **Configurable interval**: Default 30 seconds, easily adjustable
- ✅ **Comprehensive logging**: File and console logging
- ✅ **Persistent storage**: Remembers seen posts between runs
- ✅ **Error handling**: Robust error handling and recovery
- ✅ **Lightweight**: Only requires `feedparser` library

### Market Analyzer
- 🤖 **OpenAI Analysis**: Automatically analyzes each post for market impact
- 📊 **Comprehensive Market Assessment**: Covers Equities, Commodities, FX, Bonds, and Crypto
- 🎯 **Sector-Specific Analysis**: Identifies affected industries and sectors
- 📈 **Direction Prediction**: Predicts positive/negative/neutral/uncertain impact for each asset class
- 💰 **Multi-Asset Coverage**: Analyzes stocks, commodities, currencies, bonds, and crypto
- 💾 **Analysis Storage**: Saves all analyses for future reference
- 🔄 **Real-time Processing**: Analyzes new posts as they appear

### Telegram Notifications
- 📱 **Real-time Alerts**: Get instant notifications in Telegram
- 🤖 **Complete Analysis**: Receive full post content + OpenAI analysis
- 📊 **Formatted Messages**: Clean, readable message format
- 🔔 **Automatic Delivery**: No manual checking required
- 💬 **Direct to Phone**: Get alerts wherever you are

## 🚀 Quick Start

### 1. Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure APIs
```bash
# Create .env file with your API keys
echo "OPENAI_KEY=your_openai_api_key_here" > .env
echo "TELEGRAM_BOT_ID=your_telegram_bot_token" >> .env
echo "USER_ID=your_telegram_user_id" >> .env
```

### 3. Setup Telegram Bot (Optional)
1. **Create a Telegram Bot:**
   - Message [@BotFather](https://t.me/botfather) on Telegram
   - Send `/newbot` command
   - Follow instructions to create your bot
   - Copy the bot token to `TELEGRAM_BOT_ID` in `.env`

2. **Get Your User ID:**
   - Start a conversation with your bot
   - Send `/start` command
   - Visit: `https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getUpdates`
   - Find `"chat":{"id":123456789}` - that's your `USER_ID`
   - Add it to `.env` file

3. **Test Telegram Integration:**
   ```bash
   python run_analyzer.py --test
   ```

### 4. Run the tools
```bash
# Run basic RSS scraper (no analysis)
python rss_scraper.py

# Run analyzer with OpenAI market analysis + Telegram notifications
python truthsocial_analyzer.py

# Or use startup scripts
python run_scraper.py          # Basic scraper
python run_analyzer.py         # With OpenAI analysis + Telegram
```

### 5. Test first
```bash
# Test the RSS feed
python run_scraper.py --test

# Test the analyzer
python run_analyzer.py --test
```

## 📁 Files

- `rss_scraper.py` - **Basic RSS scraper** (posts only)
- `truthsocial_analyzer.py` - **Enhanced analyzer** (posts + OpenAI analysis + Telegram)
- `run_scraper.py` - Startup script for basic scraper
- `run_analyzer.py` - Startup script for analyzer
- `requirements.txt` - Python dependencies
- `seen_posts_rss.json` - Persistent storage of seen posts
- `post_analyses.json` - Stored OpenAI analyses
- `truthsocial_rss_scraper.log` - Basic scraper logs
- `truthsocial_analyzer.log` - Analyzer logs
- `README.md` - This documentation

## 🔧 Usage Options

### Basic RSS Scraper
```bash
# Run with default settings (30 seconds)
python run_scraper.py

# Custom interval (60 seconds)
python run_scraper.py --interval 60

# Test the feed
python run_scraper.py --test
```

### Market Analyzer
```bash
# Run analyzer with OpenAI analysis
python run_analyzer.py

# Custom interval (60 seconds)
python run_analyzer.py --interval 60

# Test the analyzer
python run_analyzer.py --test
```

## 📊 How It Works

### RSS Scraper
1. **RSS Feed**: Fetches posts from `https://trumpstruth.org/feed`
2. **Post Extraction**: Parses RSS entries to extract post data
3. **Deduplication**: Uses real TruthSocial post IDs (e.g., 33307, 33306)
4. **Content Display**: Shows full post content with timestamps and URLs
5. **Persistence**: Saves seen posts to avoid duplicates
6. **Monitoring**: Checks for new posts every 30 seconds

### Market Analyzer
1. **RSS Monitoring**: Same as basic scraper
2. **OpenAI Analysis**: Sends each new post to OpenAI for market impact analysis
3. **Structured Analysis**: Uses expert prompt to analyze market implications
4. **Results Display**: Shows both post content and market analysis
5. **Analysis Storage**: Saves all analyses to JSON file for future reference

## 📝 Sample Output

### Basic Scraper
```
================================================================================
🆕 NEW POST FROM @realDonaldTrump
================================================================================
📅 Time: 2025-10-14T05:36:58
🆔 Post ID: 33307
🔗 URL: https://trumpstruth.org/statuses/33307
⏰ Scraped: 2025-10-14T17:33:08.194821
================================================================================
📝 CONTENT:
================================================================================
Time Magazine wrote a relatively good story about me, but the picture may be the Worst of All Time...
================================================================================
📊 Total posts seen: 62
================================================================================
```

### Market Analyzer
```
================================================================================
🆕 NEW POST FROM @realDonaldTrump
================================================================================
📅 Time: 2025-10-14T05:36:58
🆔 Post ID: 33307
🔗 URL: https://trumpstruth.org/statuses/33307
⏰ Scraped: 2025-10-14T17:33:08.194821
================================================================================
📝 CONTENT:
================================================================================
Time Magazine wrote a relatively good story about me, but the picture may be the Worst of All Time...
================================================================================
🤖 OPENAI MARKET ANALYSIS:
================================================================================
---
**Analysis:**  
- Market Impact: No  
- Affected Markets/Sectors: None  
- Direction of Impact: N/A  
- Reasoning: This post is about media coverage and personal appearance, with no direct or indirect references to policy, trade, regulations, or economic matters that would affect financial markets.  
---
================================================================================
📊 Total posts seen: 62
📊 Total analyses: 1
================================================================================
```

### Telegram Notification
```
🆕 NEW TRUMP POST ANALYSIS

📅 Time: Tue, 14 Oct 2025 05:36:58 +0000
🆔 Post ID: 33307
🔗 URL: https://trumpstruth.org/statuses/33307

📝 POST CONTENT:
Time Magazine wrote a relatively good story about me, but the picture may be the Worst of All Time. They "disappeared" my hair, and then had something floating on top of my head that looked like a floating crown, but an extremely small one. Really weird! I never liked taking pictures from underneath angles, but this is a super bad picture, and deserves to be called out. What are they doing, and why?

🤖 MARKET ANALYSIS:
---
**Analysis:**  
- Market Impact: No

- Equities: Neutral
  - Which sectors/industries are affected? Why? None. The post does not mention any specific sector or industry.

- Commodities: Neutral
  - Which commodities are affected (e.g., oil, gold, rare earths, agriculture)? Why? None. The post does not mention any specific commodity.

- Foreign Exchange (FX): Neutral
  - Which currencies are affected (e.g., USD, CNY, EUR, JPY)? Why? None. The post does not mention any specific currency or economic policy.

- Bonds / Interest Rates: Neutral
  - Impact on Treasuries, yields, risk sentiment? None. The post does not mention any policy or event that could affect interest rates or bond markets.

- Crypto: Neutral
  - Does the post indirectly impact crypto markets (risk-on/off sentiment, regulation, etc.)? No. The post does not mention anything related to cryptocurrencies or blockchain technology.

- Reasoning: The post is a personal comment about a magazine cover and does not contain any information or sentiment that could affect financial markets.

**No material market impact expected.**
---

📊 Analyzed: 2025-10-14 18:04:35
```

## ⚙️ Customization

### Basic Scraper
Edit `rss_scraper.py`:
1. **Change interval**: Modify `interval` parameter in `run_scraper()`
2. **Custom post handling**: Modify `handle_new_post()` method
3. **Add notifications**: Extend `handle_new_post()` to send alerts

### Market Analyzer
Edit `truthsocial_analyzer.py`:
1. **Modify analysis prompt**: Change the prompt in `analyze_post_with_openai()`
2. **Change OpenAI model**: Modify `model="gpt-4"` parameter
3. **Custom analysis format**: Modify the expected output format
4. **Add more analysis**: Extend the analysis with additional metrics

### Telegram Notifications
Edit `truthsocial_analyzer.py`:
1. **Customize message format**: Modify the message template in `send_telegram_message()`
2. **Add emojis/styling**: Customize the message appearance
3. **Filter notifications**: Add conditions to only send certain types of analyses
4. **Multiple recipients**: Modify to send to multiple Telegram users

## 🔍 Why RSS + OpenAI is Perfect

- **No authentication required** - Works immediately
- **Real posts only** - No ads or promotional content
- **Reliable** - RSS feeds are designed for this purpose
- **Efficient** - Much faster than web scraping
- **Intelligent Analysis** - OpenAI provides expert-level market analysis
- **Structured Output** - Consistent, parseable analysis format
- **Historical Data** - All analyses saved for trend analysis

## 📋 Requirements

- Python 3.7+
- `feedparser` library
- `openai` library (for analyzer)
- `python-dotenv` library (for analyzer)
- `requests` library (for Telegram)
- Internet connection
- OpenAI API key (for analyzer)
- Telegram bot token (for notifications)

## ⚠️ Important Notes

- **OpenAI API Key**: Required for market analysis - set in `.env` file
- **Telegram Bot**: Optional but recommended for real-time notifications
- **API Costs**: OpenAI charges per analysis - monitor usage
- **Rate Limits**: OpenAI has rate limits - analyzer handles retries
- **Terms of Service**: Ensure compliance with TruthSocial's terms of service
- **Rate Limiting**: The 30-second interval is respectful
- **Legal Compliance**: Always respect robots.txt and terms of service
- **RSS Source**: Uses the public RSS feed from trumpstruth.org

## 🐛 Troubleshooting

### Basic Scraper Issues
1. **Check internet connection**
2. **Verify RSS feed**: Visit https://trumpstruth.org/feed
3. **Check logs**: Look at `truthsocial_rss_scraper.log`

### Analyzer Issues
1. **OpenAI API Key**: Ensure `OPENAI_KEY` is set in `.env`
2. **API Quota**: Check OpenAI billing if getting quota errors
3. **Rate Limits**: Analyzer handles retries automatically
4. **Check logs**: Look at `truthsocial_analyzer.log`

### Telegram Issues
1. **Bot Token**: Ensure `TELEGRAM_BOT_ID` is set in `.env`
2. **User ID**: Make sure you've started a conversation with your bot (`/start`)
3. **Chat Not Found**: Get your User ID from `https://api.telegram.org/bot{YOUR_BOT_TOKEN}/getUpdates`
4. **Test Integration**: Run `python run_analyzer.py --test` to verify setup
5. **Message Format**: Check for special characters that might break Markdown
6. **Rate Limits**: Telegram has rate limits for bot messages

## 🎉 Success!

This system successfully monitors Donald Trump's TruthSocial posts every 30 seconds and provides expert-level market impact analysis using OpenAI. With Telegram integration, you get real-time notifications delivered directly to your phone! It's simple, reliable, efficient, intelligent, and mobile-friendly! 🚀📱