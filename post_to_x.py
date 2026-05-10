#!/usr/bin/env python3
"""Post to X via twikit on GitHub Actions runner. ASCII-safe output."""

import asyncio, os, sys
from twikit import Client


def main():
    text = os.environ.get("TWEET_TEXT", "").strip()
    if not text:
        sys.stderr.buffer.write(b"ERROR: empty tweet text\n")
        sys.exit(1)

    cookies = {"auth_token": os.environ.get("X_AUTH_TOKEN", ""),
               "ct0": os.environ.get("X_CT0", "")}
    if os.environ.get("X_KDT"):
        cookies["kdt"] = os.environ["X_KDT"]
    if not cookies["auth_token"] or not cookies["ct0"]:
        sys.stderr.buffer.write(b"ERROR: missing cookies\n")
        sys.exit(1)

    async def post():
        client = Client(language="en-US")
        client.set_cookies(cookies)
        tweet = await client.create_tweet(text=text[:280])
        return tweet.id

    try:
        tid = asyncio.run(post())
        sys.stdout.buffer.write(f"OK tweet_id={tid}\nURL=https://x.com/user/status/{tid}\n".encode())
    except Exception as e:
        err = str(e).encode("ascii", errors="replace")
        sys.stderr.buffer.write(b"ERROR: " + err + b"\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
