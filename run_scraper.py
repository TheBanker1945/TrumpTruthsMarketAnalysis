#!/usr/bin/env python3
"""
Simple startup script for TruthSocial Scraper
This script provides an easy way to start the scraper with different options
"""

import sys
import os
import argparse

def main():
    parser = argparse.ArgumentParser(description='TruthSocial Scraper')
    parser.add_argument('--version', choices=['rss', 'enhanced', 'basic'], default='rss',
                       help='Choose scraper version (default: rss)')
    parser.add_argument('--interval', type=int, default=30,
                       help='Scraping interval in seconds (default: 30)')
    parser.add_argument('--username', default='realDonaldTrump',
                       help='TruthSocial username to scrape (default: realDonaldTrump)')
    parser.add_argument('--test', action='store_true',
                       help='Run test mode instead of continuous scraping')
    
    args = parser.parse_args()
    
    print("TruthSocial Scraper")
    print("=" * 50)
    print(f"Version: {args.version}")
    print(f"Target: @{args.username}")
    print(f"Interval: {args.interval} seconds")
    print(f"Mode: {'Test' if args.test else 'Continuous'}")
    print("=" * 50)
    
    if args.test:
        if args.version == 'rss':
            os.system(f"python -c \"from rss_scraper import TruthSocialRSSScraper; TruthSocialRSSScraper().test_feed()\"")
        elif args.version == 'enhanced':
            os.system(f"python test_enhanced_scraper.py")
        else:
            os.system(f"python test_scraper.py")
    else:
        if args.version == 'rss':
            # Import and run RSS scraper
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from rss_scraper import TruthSocialRSSScraper
            scraper = TruthSocialRSSScraper()
            scraper.run_scraper(interval=args.interval)
        elif args.version == 'enhanced':
            # Import and run enhanced scraper
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from truthsocial_scraper_enhanced import TruthSocialScraper
            scraper = TruthSocialScraper(args.username, use_selenium=True)
            scraper.run_scraper(interval=args.interval)
        else:
            # Import and run basic scraper
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from truthsocial_scraper import TruthSocialScraper
            scraper = TruthSocialScraper(args.username)
            scraper.run_scraper(interval=args.interval)

if __name__ == "__main__":
    main()
