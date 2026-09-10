from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("http://localhost:4200/login")
    page.screenshot(path="test_screenshot.png")
    print("Page title:", page.title())
    browser.close()
