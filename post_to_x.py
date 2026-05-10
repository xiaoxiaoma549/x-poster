#!/usr/bin/env python3
"""在 GitHub Actions Runner 上发推（Runner在海外，直连 x.com）"""

import asyncio
import os
import sys

# 确保 stdout 支持 Unicode
sys.stdout.reconfigure(encoding="utf-8") if hasattr(sys.stdout, "reconfigure") else None

from twikit import Client


async def main():
    text = os.environ.get("TWEET_TEXT", "").strip()
    if not text:
        print("❌ TWEET_TEXT 为空")
        sys.exit(1)

    # 从环境变量加载 cookie
    cookies = {
        "auth_token": os.environ.get("X_AUTH_TOKEN", ""),
        "ct0": os.environ.get("X_CT0", ""),
    }
    if os.environ.get("X_KDT"):
        cookies["kdt"] = os.environ["X_KDT"]

    if not cookies["auth_token"] or not cookies["ct0"]:
        print("❌ Cookie 不完整（缺少 X_AUTH_TOKEN 或 X_CT0）")
        sys.exit(1)

    client = Client(language="en-US")
    client.set_cookies(cookies)

    try:
        tweet = await client.create_tweet(text=text[:280])
        tweet_id = tweet.id
        url = f"https://x.com/user/status/{tweet_id}"
        print(f"✅ 发布成功！")
        print(f"   ID: {tweet_id}")
        print(f"   URL: {url}")
        print(f"   内容: {text[:60]}...")
    except Exception as e:
        print(f"❌ 发布失败: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
