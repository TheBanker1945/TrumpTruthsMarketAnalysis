#!/usr/bin/env python3
"""
TruthSocial RSS Scraper with OpenAI Analysis
Monitors Donald Trump's posts and analyzes them for market impact using OpenAI
"""

import feedparser
import time
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import re
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

# Load environment variables
load_dotenv('.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('truthsocial_analyzer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TruthSocialAnalyzer:
    def __init__(self, rss_url: str = "https://trumpstruth.org/feed"):
        self.rss_url = rss_url
        self.seen_posts = set()  # Track posts we've already seen
        self.posts_file = 'seen_posts_analyzer.json'
        self.analysis_file = 'post_analyses.json'
        
        # Initialize OpenAI client
        self.openai_client = None
        self.init_openai()
        
        # Initialize Telegram bot
        self.telegram_bot_token = None
        self.user_id = None
        self.init_telegram()
        
        # Load existing data
        self.load_seen_posts()
        self.load_analyses()
    
    def init_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv('OPENAI_KEY')
        if not api_key:
            logger.error("OPENAI_KEY not found in environment variables")
            logger.error("Please set OPENAI_KEY in your .env file")
            return
        
        try:
            self.openai_client = OpenAI(api_key=api_key)
            logger.info("✅ OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
    
    def init_telegram(self):
        """Initialize Telegram bot"""
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_ID')
        self.user_id = os.getenv('USER_ID')
        
        if not self.telegram_bot_token:
            logger.error("TELEGRAM_BOT_ID not found in environment variables")
            logger.error("Please set TELEGRAM_BOT_ID in your .env file")
            return
        
        if not self.user_id:
            logger.error("USER_ID not found in environment variables")
            logger.error("Please set USER_ID in your .env file")
            return
        
        logger.info("✅ Telegram bot credentials loaded successfully")
    
    def load_seen_posts(self):
        """Load previously seen posts from file"""
        try:
            with open(self.posts_file, 'r') as f:
                data = json.load(f)
                self.seen_posts = set(data.get('seen_posts', []))
                logger.info(f"Loaded {len(self.seen_posts)} previously seen posts")
        except FileNotFoundError:
            logger.info("No previous posts file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading seen posts: {e}")
    
    def save_seen_posts(self):
        """Save seen posts to file"""
        try:
            data = {
                'seen_posts': list(self.seen_posts),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.posts_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving seen posts: {e}")
    
    def load_analyses(self):
        """Load previous analyses from file"""
        try:
            with open(self.analysis_file, 'r') as f:
                self.analyses = json.load(f)
                logger.info(f"Loaded {len(self.analyses)} previous analyses")
        except FileNotFoundError:
            self.analyses = []
            logger.info("No previous analyses file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading analyses: {e}")
            self.analyses = []
    
    def save_analyses(self):
        """Save analyses to file"""
        try:
            with open(self.analysis_file, 'w') as f:
                json.dump(self.analyses, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving analyses: {e}")
    
    def fetch_rss_feed(self) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse the RSS feed"""
        try:
            logger.info(f"Fetching RSS feed from {self.rss_url}")
            feed = feedparser.parse(self.rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues: {feed.bozo_exception}")
            
            logger.info(f"Successfully fetched RSS feed with {len(feed.entries)} entries")
            return feed
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
            return None
    
    def extract_post_data(self, entry) -> Optional[Dict]:
        """Extract data from an RSS entry"""
        try:
            # Extract post ID from the link
            post_id = None
            if hasattr(entry, 'link'):
                # Extract ID from URL like https://trumpstruth.org/statuses/33307
                match = re.search(r'/statuses/(\d+)', entry.link)
                if match:
                    post_id = match.group(1)
                else:
                    # Fallback to hash of content
                    post_id = str(hash(entry.title + entry.description))
            
            # Extract post text
            post_text = ""
            if hasattr(entry, 'description'):
                # Clean up the description (remove CDATA tags and HTML)
                post_text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', entry.description)
                post_text = re.sub(r'<[^>]+>', '', post_text)  # Remove HTML tags
                post_text = post_text.strip()
            
            # Extract timestamp
            timestamp = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                timestamp = datetime(*entry.published_parsed[:6]).isoformat()
            elif hasattr(entry, 'published'):
                timestamp = entry.published
            
            # Extract URL
            post_url = entry.link if hasattr(entry, 'link') else None
            
            if post_text and len(post_text) > 10:
                return {
                    'id': post_id,
                    'text': post_text,
                    'timestamp': timestamp,
                    'url': post_url,
                    'scraped_at': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
        
        return None
    
    def analyze_post_with_openai(self, post_text: str) -> Optional[str]:
        """Analyze post using OpenAI"""
        if not self.openai_client:
            logger.error("OpenAI client not initialized")
            return None
        
        prompt = f"""You are an expert geopolitical and financial markets analyst.  
You will be given a social media post written by Donald Trump.  
Your job is to evaluate its potential market impact and produce a structured analysis.

Follow this framework exactly:

---
**Analysis:**  
- Market Impact: [Yes/No]  

- Equities: [Positive / Negative / Neutral / Uncertain]  
  - Which sectors/industries are affected? Why?  

- Commodities: [Positive / Negative / Neutral / Uncertain]  
  - Which commodities are affected (e.g., oil, gold, rare earths, agriculture)? Why?  

- Foreign Exchange (FX): [Positive / Negative / Neutral / Uncertain]  
  - Which currencies are affected (e.g., USD, CNY, EUR, JPY)? Why?  

- Bonds / Interest Rates: [Positive / Negative / Neutral / Uncertain]  
  - Impact on Treasuries, yields, risk sentiment?  

- Crypto: [Positive / Negative / Neutral / Uncertain]  
  - Does the post indirectly impact crypto markets (risk-on/off sentiment, regulation, etc.)?  

- Reasoning: [Concise explanation of why these impacts are expected.]  
---

If no material impact is expected, state clearly:  
"**No material market impact expected.**"

Post to analyze:
"{post_text}"
"""

        try:
            logger.info("🤖 Analyzing post with OpenAI...")
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert geopolitical and financial markets analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            analysis = response.choices[0].message.content.strip()
            logger.info("✅ OpenAI analysis completed")
            return analysis
            
        except Exception as e:
            logger.error(f"OpenAI analysis failed: {e}")
            if "quota" in str(e).lower() or "billing" in str(e).lower():
                logger.error("💳 OpenAI quota exceeded - please check your billing")
            return None
    
    def send_telegram_message(self, post: Dict, analysis: str):
        """Send post and analysis to Telegram using requests"""
        if not self.telegram_bot_token or not self.user_id:
            logger.warning("Telegram bot credentials not available, skipping notification")
            return
        
        try:
            # Format the message (simplified to avoid Markdown issues)
            message = f"""🆕 NEW TRUMP POST ANALYSIS

📅 Time: {post.get('timestamp', 'Unknown')}
🆔 Post ID: {post['id']}
🔗 URL: {post['url']}

📝 POST CONTENT:
{post['text']}

🤖 MARKET ANALYSIS:
{analysis}

📊 Analyzed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

            # Send the message using Telegram Bot API
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.user_id,
                'text': message
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            logger.info("✅ Telegram message sent successfully")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message: {e}")
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
    
    def check_for_new_posts(self) -> List[Dict]:
        """Check for new posts and return any new ones found"""
        feed = self.fetch_rss_feed()
        if not feed:
            return []
        
        new_posts = []
        
        for entry in feed.entries:
            post_data = self.extract_post_data(entry)
            if post_data and post_data['id'] not in self.seen_posts:
                new_posts.append(post_data)
                self.seen_posts.add(post_data['id'])
                logger.info(f"New post found: {post_data['text'][:100]}...")
        
        if new_posts:
            self.save_seen_posts()
        
        return new_posts
    
    def run_analyzer(self, interval: int = 30):
        """Run the analyzer continuously"""
        logger.info(f"Starting TruthSocial Analyzer")
        logger.info(f"RSS Feed: {self.rss_url}")
        logger.info(f"Checking for new posts every {interval} seconds")
        
        try:
            while True:
                new_posts = self.check_for_new_posts()
                
                if new_posts:
                    logger.info(f"Found {len(new_posts)} new post(s)")
                    for post in new_posts:
                        self.handle_new_post(post)
                else:
                    logger.info("No new posts found")
                
                logger.info(f"Waiting {interval} seconds before next check...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Analyzer stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.save_seen_posts()
            self.save_analyses()
    
    def handle_new_post(self, post: Dict):
        """Handle a new post - analyze and display"""
        print(f"\n{'='*80}")
        print(f"🆕 NEW POST FROM @realDonaldTrump")
        print(f"{'='*80}")
        print(f"📅 Time: {post.get('timestamp', 'Unknown')}")
        print(f"🆔 Post ID: {post['id']}")
        print(f"🔗 URL: {post['url']}")
        print(f"⏰ Scraped: {post['scraped_at']}")
        print(f"{'='*80}")
        print(f"📝 CONTENT:")
        print(f"{'='*80}")
        print(post['text'])
        print(f"{'='*80}")
        
        # Analyze with OpenAI
        analysis = self.analyze_post_with_openai(post['text'])
        
        if analysis:
            print(f"🤖 OPENAI MARKET ANALYSIS:")
            print(f"{'='*80}")
            print(analysis)
            print(f"{'='*80}")
            
            # Save analysis
            analysis_data = {
                'post_id': post['id'],
                'post_text': post['text'],
                'post_timestamp': post.get('timestamp'),
                'analysis': analysis,
                'analyzed_at': datetime.now().isoformat()
            }
            self.analyses.append(analysis_data)
            self.save_analyses()
            
            # Send to Telegram
            self.send_telegram_message(post, analysis)
        else:
            print(f"❌ Analysis failed")
        
        print(f"📊 Total posts seen: {len(self.seen_posts)}")
        print(f"📊 Total analyses: {len(self.analyses)}")
        print(f"{'='*80}\n")
        
        # Log the new post
        logger.info(f"New post processed - ID: {post['id']}, Length: {len(post['text'])} chars")
    
    def test_analyzer(self):
        """Test the analyzer with recent posts"""
        print("🧪 Testing TruthSocial Analyzer")
        print("=" * 50)
        
        feed = self.fetch_rss_feed()
        if not feed:
            print("❌ Failed to fetch RSS feed")
            return
        
        print(f"✅ Successfully fetched RSS feed")
        print(f"📊 Feed title: {feed.feed.get('title', 'Unknown')}")
        print(f"📊 Total entries: {len(feed.entries)}")
        print()
        
        print("📝 Testing analysis on recent posts:")
        for i, entry in enumerate(feed.entries[:3]):  # Test first 3 posts
            post_data = self.extract_post_data(entry)
            if post_data:
                print(f"\n--- Test Analysis {i+1} ---")
                print(f"Post: {post_data['text'][:100]}...")
                
                analysis = self.analyze_post_with_openai(post_data['text'])
                if analysis:
                    print(f"Analysis: {analysis}")
                else:
                    print("Analysis failed")

def main():
    """Main function to run the analyzer"""
    analyzer = TruthSocialAnalyzer()
    
    # Test the analyzer first
    analyzer.test_analyzer()
    
    print("\n" + "="*50)
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop")
    print("="*50)
    
    # Run the analyzer
    analyzer.run_analyzer(interval=30)

if __name__ == "__main__":
    main()
