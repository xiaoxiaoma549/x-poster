#!/usr/bin/env python3
"""在 GitHub Actions Runner 上发推（Runner在海外，直连 x.com）"""

import asyncio
import os
import sys

# 强制 stdout 用 UTF-8 — 防止 Runner locale 吃掉 Unicode
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

from twikit import Client


def out(msg):
    """安全打印，确保不含不可编码字符"""
    try:
        print(msg, flush=True)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode(), flush=True)


async def main():
    text = os.environ.get("TWEET_TEXT", "").strip()
    if not text:
        out("FAIL: TWEET_TEXT is empty")
        sys.exit(1)

    # 从环境变量加载 cookie
    cookies = {
        "auth_token": os.environ.get("X_AUTH_TOKEN", ""),
        "ct0": os.environ.get("X_CT0", ""),
    }
    if os.environ.get("X_KDT"):
        cookies["kdt"] = os.environ["X_KDT"]

    if not cookies["auth_token"] or not cookies["ct0"]:
        out("FAIL: Cookie incomplete (missing X_AUTH_TOKEN or X_CT0)")
        sys.exit(1)

    client = Client(language="en-US")
    client.set_cookies(cookies)

    try:
        tweet = await client.create_tweet(text=text[:280])
        tweet_id = tweet.id
        url = f"https://x.com/user/status/{tweet_id}"
        out(f"OK tweet_id={tweet_id}")
        out(f"URL={url}")
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
        # 清理不可编码字符
        safe_err = err.encode("ascii", errors="replace").decode()
        out(f"FAIL: {safe_err}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
