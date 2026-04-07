#!/usr/bin/env python3
"""
RSS-based TruthSocial Scraper
Uses the RSS feed from trumpstruth.org to get Donald Trump's posts
Much simpler and more reliable than web scraping!
"""

import feedparser
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import re
import supabase_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('truthsocial_rss_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TruthSocialRSSScraper:
    def __init__(self, rss_url: str = "https://trumpstruth.org/feed"):
        self.rss_url = rss_url
        self.seen_posts = supabase_client.get_seen_posts('rss')
        logger.info(f"Loaded {len(self.seen_posts)} seen posts from Supabase")
    
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
                # Clean up the description (remove CDATA tags)
                post_text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', entry.description)
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
                supabase_client.add_seen_post(post_data['id'], 'rss')
                logger.info(f"New post found: {post_data['text'][:100]}...")

        return new_posts
    
    def run_scraper(self, interval: int = 30):
        """Run the scraper continuously"""
        logger.info(f"Starting RSS-based TruthSocial scraper")
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
            logger.info("Scraper stopped by user")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            logger.info("Scraper shutting down")
    
    def handle_new_post(self, post: Dict):
        """Handle a new post - customize this method for your needs"""
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
        print(f"📊 Total posts seen: {len(self.seen_posts)}")
        print(f"{'='*80}\n")
        
        # Log the new post
        logger.info(f"New post detected - ID: {post['id']}, Length: {len(post['text'])} chars")
    
    def test_feed(self):
        """Test the RSS feed and show recent posts"""
        print("🧪 Testing RSS Feed")
        print("=" * 50)
        
        feed = self.fetch_rss_feed()
        if not feed:
            print("❌ Failed to fetch RSS feed")
            return
        
        print(f"✅ Successfully fetched RSS feed")
        print(f"📊 Feed title: {feed.feed.get('title', 'Unknown')}")
        print(f"📊 Total entries: {len(feed.entries)}")
        print()
        
        print("📝 Recent posts:")
        for i, entry in enumerate(feed.entries[:5]):  # Show first 5 posts
            post_data = self.extract_post_data(entry)
            if post_data:
                print(f"\nPost {i+1}:")
                print(f"  ID: {post_data['id']}")
                print(f"  Time: {post_data.get('timestamp', 'Unknown')}")
                print(f"  Text: {post_data['text'][:100]}...")
                print(f"  URL: {post_data['url']}")

def main():
    """Main function to run the RSS scraper"""
    scraper = TruthSocialRSSScraper()
    
    # Test the feed first
    scraper.test_feed()
    
    print("\n" + "="*50)
    print("Starting continuous monitoring...")
    print("Press Ctrl+C to stop")
    print("="*50)
    
    # Run the scraper
    scraper.run_scraper(interval=30)

if __name__ == "__main__":
    main()
