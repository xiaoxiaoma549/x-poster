#!/usr/bin/env python3
"""Post to X via twikit. Writes result to /tmp/xpost_result."""
import asyncio, io, os, sys

# Isolate ALL output to /dev/null
devnull = open("/dev/null", "w")
sys.stdout = devnull
sys.stderr = devnull

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
    with open("/tmp/xpost_result", "w") as f:
        f.write(f"OK tweet_id={tid}\n")
        f.write(f"URL=https://x.com/user/status/{tid}\n")
except Exception as e:
    err = str(e).encode("ascii", errors="replace").decode()
    with open("/tmp/xpost_result", "w") as f:
        f.write(f"ERROR: {err}\n")
    exit(1)
