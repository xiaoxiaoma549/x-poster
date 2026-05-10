#!/usr/bin/env python3
"""Post to X via twikit on GitHub Actions runner (no proxy needed)."""

import asyncio
import os
import sys

from twikit import Client


async def main():
    text = os.environ.get("TWEET_TEXT", "").strip()
    if not text:
        print("ERROR: empty tweet text")
        sys.exit(1)

    cookies = {"auth_token": os.environ.get("X_AUTH_TOKEN", ""),
               "ct0": os.environ.get("X_CT0", "")}
    if os.environ.get("X_KDT"):
        cookies["kdt"] = os.environ["X_KDT"]

    if not cookies["auth_token"] or not cookies["ct0"]:
        print("ERROR: missing cookies")
        sys.exit(1)

    client = Client(language="en-US")
    client.set_cookies(cookies)

    try:
        tweet = await client.create_tweet(text=text[:280])
        print(f"OK tweet_id={tweet.id}")
        print(f"URL=https://x.com/user/status/{tweet.id}")
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
