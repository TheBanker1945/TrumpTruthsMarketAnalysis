"""
Supabase client for persistent storage of seen posts and analyses.

Supabase SQL setup — run this in the Supabase SQL Editor:

    CREATE TABLE seen_posts (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        post_id TEXT NOT NULL,
        source TEXT NOT NULL,
        created_at TIMESTAMPTZ DEFAULT NOW(),
        UNIQUE (post_id, source)
    );

    CREATE TABLE post_analyses (
        id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        post_id TEXT NOT NULL,
        post_text TEXT NOT NULL,
        post_timestamp TEXT,
        analysis TEXT NOT NULL,
        analyzed_at TIMESTAMPTZ NOT NULL
    );
"""

import os
import logging
from supabase import create_client, Client

logger = logging.getLogger(__name__)

_client: Client | None = None


def _get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        _client = create_client(url, key)
        logger.info("Supabase client initialized successfully")
    return _client


def get_seen_posts(source: str) -> set[str]:
    """Return the set of post IDs already seen for the given source ('analyzer' or 'rss')."""
    response = (
        _get_client()
        .table("seen_posts")
        .select("post_id")
        .eq("source", source)
        .execute()
    )
    return {row["post_id"] for row in response.data}


def add_seen_post(post_id: str, source: str) -> None:
    """Insert a seen post. Ignores duplicates."""
    _get_client().table("seen_posts").upsert(
        {"post_id": post_id, "source": source},
        on_conflict="post_id,source",
    ).execute()


def get_analyses() -> list[dict]:
    """Return all stored analyses ordered by analyzed_at."""
    response = (
        _get_client()
        .table("post_analyses")
        .select("*")
        .order("analyzed_at", desc=False)
        .execute()
    )
    return response.data


def add_analysis(
    post_id: str,
    post_text: str,
    post_timestamp: str | None,
    analysis: str,
    analyzed_at: str,
) -> None:
    """Insert a new analysis record."""
    _get_client().table("post_analyses").insert(
        {
            "post_id": post_id,
            "post_text": post_text,
            "post_timestamp": post_timestamp,
            "analysis": analysis,
            "analyzed_at": analyzed_at,
        }
    ).execute()
