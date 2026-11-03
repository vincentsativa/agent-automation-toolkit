#!/usr/bin/env python3
"""Screenshot HTML mockup files using Playwright. Run from the mockup directory."""
import asyncio
import glob
import os
import sys
from playwright.async_api import async_playwright

async def screenshot_page(url, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto(url, wait_until="networkidle")
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
        print(f"Saved: {output_path}")

async def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "."
    html_files = sorted(glob.glob(os.path.join(directory, "*.html")))
    if not html_files:
        print("No HTML files found.")
        return
    for html_file in html_files:
        abs_path = os.path.abspath(html_file)
        png_path = abs_path.replace(".html", ".png")
        await screenshot_page(f"file://{abs_path}", png_path)

asyncio.run(main())