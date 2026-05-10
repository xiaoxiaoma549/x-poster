#!/usr/bin/env python3
"""Post to X - full patch for httpx + client_transaction bypass."""
import asyncio, os, sys, time, json

# Patch 1: httpx Headers encoding
import httpx._models as _m
_orig_init_h = _m.Headers.__init__
def _patched_init_h(self, headers=None, encoding=None):
    if encoding is None: encoding = "utf-8"
    _orig_init_h(self, headers, encoding)
_m.Headers.__init__ = _patched_init_h

# Patch 2: Skip client_transaction init entirely
import twikit.client.client as _cc
_orig_request = _cc.Client.request
async def _patched_request(self, method, url, auto_unlock=True, raise_exception=True, **kwargs):
    headers = kwargs.pop("headers", {})
    cookies_backup = self.get_cookies().copy()
    response = await self.http.request(method, url, headers=headers, **kwargs)
    self._remove_duplicate_ct0_cookie()
    try:
        response_data = response.json()
    except json.decoder.JSONDecodeError:
        response_data = response.text
    if isinstance(response_data, dict) and "errors" in response_data:
        error_code = response_data["errors"][0]["code"]
        error_message = response_data["errors"][0].get("message")
        if error_code in (37, 64):
            from twikit.errors import AccountSuspended
            raise AccountSuspended(error_message)
        if error_code == 326:
            from twikit.errors import AccountLocked
            raise AccountLocked("Account locked.")
    status_code = response.status_code
    if status_code >= 400 and raise_exception:
        message = f'status: {status_code}, message: "{response.text}"'
        if status_code == 400:
            from twikit.errors import BadRequest
            raise BadRequest(message, headers=response.headers)
        elif status_code == 401:
            from twikit.errors import Unauthorized
            raise Unauthorized(message, headers=response.headers)
        elif status_code == 403:
            from twikit.errors import Forbidden
            raise Forbidden(message, headers=response.headers)
        elif status_code == 429:
            from twikit.errors import TooManyRequests
            raise TooManyRequests(message, headers=response.headers)
        elif 500 <= status_code < 600:
            from twikit.errors import ServerError
            raise ServerError(message, headers=response.headers)
        else:
            from twikit.errors import TwitterException
            raise TwitterException(message, headers=response.headers)
    if status_code == 200:
        return response_data, response
    return response_data, response
_cc.Client.request = _patched_request

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
