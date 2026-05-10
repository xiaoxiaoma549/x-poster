#!/usr/bin/env python3
"""Post to X - with httpx encoding patch."""
import asyncio, os, sys

# Patch httpx to never use ascii encoding for headers
import httpx._models as _models
_orig_init = _models.Headers.__init__
def _patched_init(self, headers=None, encoding=None):
    if encoding is None:
        encoding = "utf-8"
    _orig_init(self, headers, encoding)
_models.Headers.__init__ = _patched_init

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
