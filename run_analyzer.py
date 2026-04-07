#!/usr/bin/env python3
"""
Startup script for TruthSocial Analyzer
Easy way to run the analyzer with different options
"""

import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

def main():
    parser = argparse.ArgumentParser(description='TruthSocial Analyzer')
    parser.add_argument('--interval', type=int, default=30,
                       help='Analysis interval in seconds (default: 30)')
    parser.add_argument('--test', action='store_true',
                       help='Run test mode instead of continuous monitoring')
    parser.add_argument('--once', action='store_true',
                       help='Run a single check cycle then exit (for scheduled/cron execution)')

    args = parser.parse_args()

    mode = 'Test' if args.test else ('Single check' if args.once else 'Continuous')
    print("TruthSocial Analyzer")
    print("=" * 50)
    print(f"Interval: {args.interval} seconds")
    print(f"Mode: {mode}")
    print("=" * 50)
    
    # Check for Anthropic API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set ANTHROPIC_API_KEY in your .env file")
        return
    
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from truthsocial_analyzer import TruthSocialAnalyzer
    analyzer = TruthSocialAnalyzer()

    if args.test:
        analyzer.test_analyzer()
    elif args.once:
        analyzer.run_once()
    else:
        analyzer.run_analyzer(interval=args.interval)

if __name__ == "__main__":
    main()
