# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python bot that monitors Donald Trump's TruthSocial posts via RSS feed (`trumpstruth.org/feed`) and analyzes them for financial market impact using the Anthropic Claude API. Posts with market impact are forwarded as Telegram notifications.

## Commands

```bash
# Setup
source venv/bin/activate
pip install -r requirements.txt

# Run the analyzer (Claude analysis + Telegram notifications)
python run_analyzer.py                  # continuous monitoring (30s default)
python run_analyzer.py --interval 60    # custom interval
python run_analyzer.py --test           # test mode: analyze 3 recent posts then exit

# Run the basic RSS scraper (no analysis, just displays posts)
python run_scraper.py                   # continuous monitoring
python run_scraper.py --test            # test mode
```

No test suite exists. The `--test` flags run integration tests against the live RSS feed and APIs.

## Architecture

Two parallel systems share the same RSS source (`trumpstruth.org/feed`) but operate independently:

- **`rss_scraper.py`** (`TruthSocialRSSScraper`) — Standalone scraper that fetches and displays posts. Only needs Supabase credentials.

- **`truthsocial_analyzer.py`** (`TruthSocialAnalyzer`) — Full pipeline: fetch RSS → analyze with Claude (`claude-sonnet-4-6`) → send Telegram alert if market impact detected. Needs all env vars.

- **`supabase_client.py`** — Persistence layer wrapping Supabase. Provides `get_seen_posts()`, `add_seen_post()`, `get_analyses()`, `add_analysis()`. Contains the SQL table creation statements in its module docstring.

- **`run_analyzer.py` / `run_scraper.py`** — CLI entry points with argparse (`--interval`, `--test`).

### Persistence (Supabase)

Two tables, both defined in `supabase_client.py` docstring:

- **`seen_posts`** — Deduplication. Has a `source` column (`'analyzer'` or `'rss'`) so the two scrapers track seen posts independently via a `UNIQUE (post_id, source)` constraint. Each scraper loads its own set on startup and writes per-post as they're discovered.

- **`post_analyses`** — Stores Claude analysis results. Only written by the analyzer.

The client uses a lazy singleton pattern (`_get_client()`). RLS must be disabled on both tables for the anon key to work.

### Analysis flow

1. `check_for_new_posts()` fetches RSS, deduplicates against in-memory `seen_posts` set
2. `handle_new_post()` calls `analyze_post_with_claude()` — structured prompt asking Claude to evaluate market impact across equities, commodities, FX, bonds, and crypto
3. `has_market_impact()` regex-checks for `market impact: yes` (case-insensitive)
4. Only "yes" posts trigger `send_telegram_message()` via `requests.post()` to the Telegram Bot API

### Telegram

Notifications use `requests.post()` directly against the Telegram Bot API — **not** the `python-telegram-bot` library (which is in `requirements.txt` but unused).

## Environment Variables

Configured in `.env` (see `.env.example`):
- `ANTHROPIC_API_KEY` — required for the analyzer
- `TELEGRAM_BOT_ID` — Telegram bot token for notifications
- `USER_ID` — Telegram chat ID for message delivery
- `SUPABASE_URL` — Supabase project URL (required for both scraper and analyzer)
- `SUPABASE_KEY` — Supabase anon key (required; RLS must be disabled on tables)

## Known Discrepancies

- The README still references OpenAI in many places but the codebase uses Anthropic Claude.
- `run_scraper.py` accepts `--version enhanced` and `--version basic` but those scraper modules don't exist. Only `--version rss` (the default) works.
- `python-telegram-bot` is in requirements.txt but Telegram calls use `requests` directly.
