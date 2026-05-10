#!/usr/bin/env python3
"""Post to X via subprocess with clean UTF-8 environment."""
import asyncio, json, os, subprocess, sys

text = os.environ["TWEET_TEXT"]

# Run twikit in a subprocess with LANG=C.UTF-8
env = {
    "TWEET_TEXT": text,
    "AUTH_TOKEN": os.environ["AUTH_TOKEN"],
    "CT0": os.environ["CT0"],
    "KDT": os.environ.get("KDT", ""),
    "LANG": "C.UTF-8",
    "LC_ALL": "C.UTF-8",
    "PYTHONUTF8": "1",
    "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
}

code = """
import asyncio, os, sys
sys.stdout = open('/dev/null', 'w')
sys.stderr = open('/dev/null', 'w')
from twikit import Client

async def post():
    c = Client(language='en-US')
    c.set_cookies({'auth_token': os.environ['AUTH_TOKEN'], 'ct0': os.environ['CT0']})
    if os.environ.get('KDT'): c.set_cookies({'auth_token': os.environ['AUTH_TOKEN'], 'ct0': os.environ['CT0'], 'kdt': os.environ['KDT']})
    t = await c.create_tweet(text=os.environ['TWEET_TEXT'][:280])
    return t.id

try:
    tid = asyncio.run(post())
    with open('/tmp/xpost_r', 'w') as f: f.write(f'OK {tid}')
except Exception as e:
    with open('/tmp/xpost_r', 'w') as f: f.write(f'ERR {e}')
"""

result = subprocess.run(
    ["python3", "-c", code],
    capture_output=True, text=True,
    env=env, timeout=60,
)

# Read result file
try:
    with open("/tmp/xpost_r") as f:
        line = f.read().strip()
    if line.startswith("OK "):
        tid = line[3:]
        print(f"OK tweet_id={tid}")
        print(f"URL=https://x.com/user/status/{tid}")
    else:
        print(f"ERROR: {line[4:]}")
        exit(1)
except FileNotFoundError:
    print(f"ERROR: no result file. stdout={result.stdout} stderr={result.stderr}")
    exit(1)
