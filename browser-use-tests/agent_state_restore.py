"""
Browser state restore script - Load saved session state and navigate.

This script loads a previously saved browser state (cookies, localStorage, sessionStorage)
from a JSON file and navigates to the target page with the restored session. The filename
is automatically generated from the URL and username.

Usage:
    uv run agent_state_restore.py --url https://example.com --username user
"""

import argparse
import asyncio
import json
import re
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from playwright.async_api import async_playwright

load_dotenv()

# Directory where browser states are stored
BROWSER_STATES_DIR = Path(__file__).parent / "browser_states"


def generate_state_name(url: str, username: str) -> str:
    """Generate a state filename from URL and username."""
    # Extract domain from URL
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    # Clean domain and username to be filesystem-safe
    domain_clean = re.sub(r'[^\w\-.]', '_', domain)
    username_clean = re.sub(r'[^\w\-.]', '_', username)
    return f"{domain_clean}_{username_clean}"


async def restore_browser_state(
    url: str,
    username: str,
    headless: bool = False,
    keep_open: bool = True
) -> None:
    """Load a saved browser state and navigate to the target URL."""
    
    # Generate state name from URL and username
    state_name = generate_state_name(url, username)
    state_file = BROWSER_STATES_DIR / f"{state_name}.json"
    
    # Check if state file exists
    if not state_file.exists():
        print(f"✗ Error: State file not found: {state_file}")
        print(f"\nAvailable states in {BROWSER_STATES_DIR}:")
        states = list(BROWSER_STATES_DIR.glob("*.json"))
        if states:
            for s in states:
                print(f"  - {s.stem}")
        else:
            print("  (none)")
        return
    
    print("=" * 70)
    print("Browser State Restore Script")
    print("=" * 70)
    print(f"State file: {state_file}")
    print(f"Target URL: {url}")
    print("=" * 70)
    
    # Load the saved state
    try:
        storage_state = json.loads(state_file.read_text())
        cookies = storage_state.get('cookies', [])
        origins = storage_state.get('origins', [])
        
        print(f"✓ Loaded state from {state_file}")
        print(f"  - {len(cookies)} cookies")
        print(f"  - {len(origins)} origins with localStorage/sessionStorage")
        
    except Exception as e:
        print(f"✗ Error loading state file: {e}")
        return
    
    # Launch browser with Playwright directly for more control
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=headless,
            args=[
                '--no-sandbox',
                '--disable-blink-features=AutomationControlled',
            ]
        )
        
        # Create a new context (use storage_state if Playwright supports it directly)
        # Note: Playwright's storage_state format is compatible
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            storage_state=storage_state if cookies else None,
        )
        
        page = await context.new_page()
        
        try:
            print("\n" + "-" * 70)
            print("Restoring browser state...")
            
            # If we have cookies but didn't use storage_state, add them manually
            if cookies and not storage_state:
                await context.add_cookies(cookies)
                print(f"✓ Added {len(cookies)} cookies")
            
            # Navigate to the target URL
            print(f"Navigating to {url}...")
            await page.goto(url, wait_until='networkidle')
            
            # Set localStorage and sessionStorage if present
            if origins:
                for origin_data in origins:
                    origin_url = origin_data.get('origin', url)
                    
                    # Set localStorage items
                    if 'localStorage' in origin_data:
                        for item in origin_data['localStorage']:
                            await page.evaluate(
                                f"window.localStorage.setItem({json.dumps(item['name'])}, {json.dumps(item['value'])});"
                            )
                        print(f"✓ Set {len(origin_data['localStorage'])} localStorage items for {origin_url}")
                    
                    # Set sessionStorage items
                    if 'sessionStorage' in origin_data:
                        for item in origin_data['sessionStorage']:
                            await page.evaluate(
                                f"window.sessionStorage.setItem({json.dumps(item['name'])}, {json.dumps(item['value'])});"
                            )
                        print(f"✓ Set {len(origin_data['sessionStorage'])} sessionStorage items for {origin_url}")
                
                # Refresh to apply storage changes
                print("Refreshing page to apply storage changes...")
                await page.reload(wait_until='networkidle')
            
            print("-" * 70)
            print("✓ Browser state restored successfully!")
            print(f"✓ Navigated to {url}")
            print(f"\nCurrent URL: {page.url}")
            
            # Get page title for verification
            title = await page.title()
            print(f"Page title: {title}")
            
            if keep_open:
                print("\n" + "=" * 70)
                print("Browser is ready. Press Ctrl+C to close...")
                print("=" * 70)
                
                # Keep the browser open until interrupted
                stop_event = asyncio.Event()
                try:
                    await stop_event.wait()
                except KeyboardInterrupt:
                    print("\nClosing browser...")
            else:
                # Wait a bit to see the result
                await asyncio.sleep(3)
            
        finally:
            await context.close()
            await browser.close()
            print("✓ Browser closed")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load saved browser state and navigate to page (filename auto-generated from URL and username)"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Target URL to navigate to",
    )
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Username (used to find the saved state file)",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--no-keep-open",
        action="store_true",
        help="Close browser after navigation (default: keep open)",
    )
    
    args = parser.parse_args()
    
    asyncio.run(
        restore_browser_state(
            url=args.url,
            username=args.username,
            headless=args.headless,
            keep_open=not args.no_keep_open,
        )
    )


if __name__ == "__main__":
    main()
