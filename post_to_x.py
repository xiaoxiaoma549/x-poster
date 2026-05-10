#!/usr/bin/env python3
"""Post to X via Playwright on GitHub Actions runner. Debug version."""
import json, os, sys, base64
from playwright.sync_api import sync_playwright

text = os.environ["TWEET_TEXT"].strip()[:280]
cookie_vals = {
    "auth_token": os.environ["AUTH_TOKEN"],
    "ct0": os.environ["CT0"],
    "kdt": os.environ.get("KDT", ""),
}

with sync_playwright() as p:
    # Use full chromium, not headless shell
    browser = p.chromium.launch(
        channel="chromium",
        headless=True,
        args=["--disable-blink-features=AutomationControlled",
              "--no-sandbox",
              "--disable-setuid-sandbox"],
    )
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36",
        locale="en-US",
        timezone_id="America/New_York",
    )
    page = ctx.new_page()

    # Navigate to x.com
    page.goto("https://x.com", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    print(f"Step1 url={page.url}", flush=True)

    # Inject cookies via Playwright API
    ctx.add_cookies([
        {"name": k, "value": v, "domain": ".x.com", "path": "/"}
        for k, v in cookie_vals.items() if v
    ])

    # Also inject via JS for good measure
    for k, v in cookie_vals.items():
        if v:
            page.evaluate(f"document.cookie='{k}={v};domain=.x.com;path=/;secure'")

    # Go to home page
    page.goto("https://x.com/home", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    print(f"Step2 url={page.url}", flush=True)
    print(f"Step2 title={page.title()[:80]}", flush=True)

    # Screenshot for debug
    screenshot = page.screenshot()
    with open("/tmp/debug_x.png", "wb") as f:
        f.write(screenshot)
    print(f"Step2 screenshot saved", flush=True)

    # Check login
    if "login" in page.url or "i/flow" in page.url:
        print("ERROR: cookie expired / login required", flush=True)
        browser.close()
        sys.exit(1)

    # Check if home page loaded (has timeline)
    timeline = page.query_selector('div[data-testid="primaryColumn"]')
    if not timeline:
        print("WARNING: no primary column found, maybe not logged in", flush=True)

    # Go to compose
    page.goto("https://x.com/compose/post", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    print(f"Step3 url={page.url}", flush=True)
    print(f"Step3 content snippet: {page.content()[:500]}", flush=True)

    # Find text input
    textarea = None
    for sel in [
        'div[data-testid="tweetTextarea_0"]',
        'div[role="textbox"]',
        'div[contenteditable="true"]',
    ]:
        try:
            el = page.wait_for_selector(sel, timeout=2000)
            if el:
                textarea = el
                print(f"Found input: {sel}", flush=True)
                break
        except:
            continue

    if not textarea:
        print("ERROR: no text input found", flush=True)
        browser.close()
        sys.exit(1)

    textarea.click()
    page.wait_for_timeout(300)
    textarea.fill(text)
    page.wait_for_timeout(500)

    # Post button
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
                print(f"Clicked: {sel}", flush=True)
                break
        except:
            continue

    if not posted:
        print("ERROR: no post button found", flush=True)
        browser.close()
        sys.exit(1)

    page.wait_for_timeout(3000)
    tb = page.query_selector('div[data-testid="tweetTextarea_0"]')
    if tb and not tb.inner_text().strip():
        print(f"OK tweet posted", flush=True)
    else:
        print("WARNING: result uncertain", flush=True)

    browser.close()
