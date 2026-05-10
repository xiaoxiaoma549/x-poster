#!/usr/bin/env python3
"""Post to X - with httpx encoding patch + bypass KEY_BYTE."""
import asyncio, os, sys

# Patch httpx
import httpx._models as _m
_orig_init = _m.Headers.__init__
def _patched_init(self, headers=None, encoding=None):
    if encoding is None:
        encoding = "utf-8"
    _orig_init(self, headers, encoding)
_m.Headers.__init__ = _patched_init

# Bypass twikit's client_transaction KEY_BYTE check
import twikit.x_client_transaction.transaction as ct
_orig_get_indices = ct.ClientTransaction.get_indices
async def _patched_get_indices(self, *a, **kw):
    try:
        return await _orig_get_indices(self, *a, **kw)
    except Exception:
        self.DEFAULT_ROW_INDEX = 0
        self.DEFAULT_KEY_BYTES_INDICES = [0]
        return 0, [0]
ct.ClientTransaction.get_indices = _patched_get_indices

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
