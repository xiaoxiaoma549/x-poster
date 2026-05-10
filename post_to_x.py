#!/usr/bin/env python3
"""Post to X - httpx patch + fake X-Client-Transaction-Id."""
import asyncio, os, sys, time, hashlib

# Patch httpx Headers encoding to utf-8
import httpx._models as _m
_orig_h = _m.Headers.__init__
def _patched_h(self, headers=None, encoding=None):
    if encoding is None: encoding = "utf-8"
    _orig_h(self, headers, encoding)
_m.Headers.__init__ = _patched_h

# Bypass KEY_BYTE + generate fake transaction ID
import twikit.x_client_transaction.transaction as _ct
_orig_init = _ct.ClientTransaction.init
async def _patched_init(self, session, headers):
    # Just set a dummy home_page response to skip KEY_BYTE processing
    import bs4
    self.home_page_response = bs4.BeautifulSoup("<html></html>", "lxml")
    self.DEFAULT_ROW_INDEX = 0
    self.DEFAULT_KEY_BYTES_INDICES = [0, 1, 2, 3]
    import twikit.x_client_transaction.utils as _utils
    self.key = hashlib.md5(str(time.time()).encode()).hexdigest()
    self.key_bytes = self.key.encode()
    self.animation_key = [0.5, 0.5, 0.5]
_ct.ClientTransaction.init = _patched_init

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
