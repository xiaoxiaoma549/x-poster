#!/usr/bin/env python3
"""Post to X via twikit. Suppress all stdout during twikit call."""
import asyncio, io, os, sys

from twikit import Client

text = os.environ["TWEET_TEXT"]
cookies = {"auth_token": os.environ["AUTH_TOKEN"], "ct0": os.environ["CT0"]}
if os.environ.get("KDT"): cookies["kdt"] = os.environ["KDT"]

async def post():
    c = Client(language="en-US")
    c.set_cookies(cookies)
    t = await c.create_tweet(text=text[:280])
    return t.id

# Temporarily suppress all stdout to prevent twikit internal encoding errors
old_out = sys.stdout
old_err = sys.stderr
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()

try:
    tid = asyncio.run(post())
    sys.stdout = old_out
    sys.stderr = old_err
    print(f"OK tweet_id={tid}", flush=True)
    print(f"URL=https://x.com/user/status/{tid}", flush=True)
except Exception as e:
    sys.stdout = old_out
    sys.stderr = old_err
    err = str(e).encode("ascii", errors="replace").decode()
    print(f"ERROR: {err}", flush=True)
    exit(1)
