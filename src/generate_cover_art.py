import sys
from playwright.sync_api import sync_playwright

html_path = sys.argv[1]
query_string = sys.argv[2]
selector = sys.argv[3]
output_path = sys.argv[4]
url = f"file://{html_path}?{query_string}"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.goto(url)
    element = page.wait_for_selector(selector)
    element.screenshot(path=output_path)

    browser.close()
