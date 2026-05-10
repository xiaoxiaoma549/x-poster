#!/usr/bin/env python3
"""Post to X via direct GraphQL API call. No twikit dependency."""
import json, os, subprocess, sys

text = os.environ["TWEET_TEXT"][:280]
auth_token = os.environ["AUTH_TOKEN"]
ct0 = os.environ["CT0"]
kdt = os.environ.get("KDT", "")

# Use curl for the GraphQL call (no Python encoding issues at all)
payload = json.dumps({
    "variables": {
        "tweet_text": text,
        "dark_request": False,
        "media": {"media_entities": [], "possibly_sensitive": False},
        "semantic_annotation_ids": {}
    },
    "queryId": "47mfhSw7D4cm48ljEBV_7w"
})

cookie = f"auth_token={auth_token}; ct0={ct0}"
if kdt:
    cookie += f"; kdt={kdt}"

bearer = "AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs=1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"

result = subprocess.run([
    "curl", "-s", "-w", "\n%{http_code}",
    "-H", f"Authorization: Bearer {bearer}",
    "-H", f"X-CSRF-Token: {ct0}",
    "-H", f"Cookie: {cookie}",
    "-H", "Content-Type: application/json",
    "-H", "User-Agent: Mozilla/5.0 (X11; Linux x86_64)",
    "-H", "Origin: https://x.com",
    "-H", "Referer: https://x.com/",
    "-d", payload,
    "https://x.com/i/api/graphql/47mfhSw7D4cm48ljEBV_7w/CreateTweet"
], capture_output=True, text=True, timeout=30)

lines = result.stdout.strip().split("\n")
http_code = lines[-1].strip()
body = "\n".join(lines[:-1])

if http_code == "200":
    try:
        data = json.loads(body)
        tid = data["data"]["create_tweet"]["tweet_results"]["result"]["rest_id"]
        print(f"OK tweet_id={tid}")
        print(f"URL=https://x.com/user/status/{tid}")
    except (KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: parse failed: {e}")
        print(f"BODY: {body[:200]}")
        exit(1)
else:
    print(f"ERROR: HTTP {http_code}")
    print(f"BODY: {body[:300]}")
    exit(1)
