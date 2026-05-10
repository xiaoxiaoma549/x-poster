#!/usr/bin/env python3
"""Post to X via twikit - httpx patch + upgrade."""
import asyncio, os, sys

# Patch httpx Headers encoding to utf-8
import httpx._models as _m
_orig = _m.Headers.__init__
_m.Headers.__init__ = lambda self, h=None, e=None: _orig(self, h, e or "utf-8")

from twikit import Client

text = os.environ["TWEET_TEXT"]
cookies = {"auth_token": os.environ["AUTH_TOKEN"], "ct0": os.environ["CT0"]}
if os.environ.get("KDT"): cookies["kdt"] = os.environ["KDT"]

async def post():
    c = Client(language="en-US")
    c.set_cookies(cookies)
    t = await c.create_tweet(text=text[:280])
    return t.id

try:
    tid = asyncio.run(post())
    print(f"OK tweet_id={tid}")
    print(f"URL=https://x.com/user/status/{tid}")
except Exception as e:
    import traceback
    traceback.print_exc()
    exit(1)
