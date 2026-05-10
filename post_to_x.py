#!/usr/bin/env python3
"""Post to X via Playwright on GitHub Actions runner (USA, no proxy)."""
import json, os, sys, time
from playwright.sync_api import sync_playwright

text = os.environ["TWEET_TEXT"].strip()[:280]
cookies = {
    "auth_token": os.environ["AUTH_TOKEN"],
    "ct0": os.environ["CT0"],
    "kdt": os.environ.get("KDT", ""),
}

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=["--disable-blink-features=AutomationControlled",
              "--no-sandbox"],
    )
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent=(
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
    )
    page = ctx.new_page()

    # 1. Go to x.com to establish session
    page.goto("https://x.com", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)

    # 2. Inject cookies
    ctx.add_cookies([
        {"name": k, "value": v, "domain": ".x.com", "path": "/"}
        for k, v in cookies.items() if v
    ])

    # 3. Refresh to activate cookies
    page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    # 4. Check login status
    if "login" in page.url or "i/flow" in page.url:
        print("ERROR: cookie expired / login required")
        browser.close()
        sys.exit(1)

    # 5. Go to compose page
    page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)

    # 6. Find text input and type tweet
    textarea = None
    for sel in [
        'div[data-testid="tweetTextarea_0"]',
        'div[role="textbox"]',
        'div[contenteditable="true"]',
    ]:
        try:
            textarea = page.wait_for_selector(sel, timeout=3000)
            if textarea:
                break
        except:
            continue

    if not textarea:
        print("ERROR: no text input found")
        browser.close()
        sys.exit(1)

    textarea.click()
    page.wait_for_timeout(300)
    textarea.fill(text)
    page.wait_for_timeout(500)

    # 7. Click post button
    posted = False
    for sel in [
        'div[data-testid="tweetButtonInline"]',
        'button[data-testid="tweetButton"]',
    ]:
        try:
            btn = page.wait_for_selector(sel, timeout=3000)
            if btn and btn.is_enabled():
                btn.click()
                posted = True
                break
        except:
            continue

    if not posted:
        print("ERROR: no post button found")
        browser.close()
        sys.exit(1)

    # 8. Wait and verify
    page.wait_for_timeout(3000)
    after_url = page.url
    tb = page.query_selector('div[data-testid="tweetTextarea_0"]')
    if tb and not tb.inner_text().strip():
        print(f"OK tweet posted")
        print(f"URL check: {after_url}")
    else:
        print("WARNING: may or may not have posted, check manually")

    browser.close()
