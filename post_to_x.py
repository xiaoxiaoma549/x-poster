#!/usr/bin/env python3
"""Post to X via Playwright - construct cookies from env vars."""
import json, os, sys, time
from playwright.sync_api import sync_playwright

text = os.environ["TWEET_TEXT"].strip()[:280]

# Construct cookies dict from env vars
cookies = {
    "auth_token": os.environ["AUTH_TOKEN"],
    "ct0": os.environ["CT0"],
    "kdt": os.environ.get("KDT", ""),
    "twid": "u%3D2964013343",
    "guest_id": "v1%3A176000596429292473",
    "lang": "en",
}

with sync_playwright() as p:
    browser = p.chromium.launch(
        channel="chromium",
        headless=True,
        args=["--disable-blink-features=AutomationControlled",
              "--no-sandbox"],
    )
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        locale="en-US",
    )
    page = ctx.new_page()

    # Add cookies before navigation
    ctx.add_cookies([
        {"name": k, "value": v, "domain": "x.com", "path": "/"}
        for k, v in cookies.items() if v
    ])

    # Navigate to home
    page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(5000)

    if "login" in page.url or "i/flow" in page.url:
        print("ERROR: login required")
        browser.close()
        sys.exit(1)

    # Compose
    page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    textarea = (page.query_selector('div[data-testid="tweetTextarea_0"]')
                or page.query_selector('div[role="textbox"]')
                or page.query_selector('div[contenteditable="true"]'))
    if not textarea:
        print("ERROR: no text input")
        browser.close()
        sys.exit(1)

    textarea.click()
    page.wait_for_timeout(300)
    textarea.fill(text)
    page.wait_for_timeout(500)

    btn = (page.query_selector('div[data-testid="tweetButtonInline"]')
           or page.query_selector('button[data-testid="tweetButton"]'))
    if not btn:
        print("ERROR: no post button")
        browser.close()
        sys.exit(1)

    btn.click()
    page.wait_for_timeout(3000)
    print("OK tweet attempted")
    browser.close()
