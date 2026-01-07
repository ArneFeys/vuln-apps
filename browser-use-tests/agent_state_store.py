"""
Browser state storage script - Login and save session state.

This script logs into a website and saves the browser state (cookies, localStorage, 
sessionStorage) to a JSON file in the browser_states folder. The filename is automatically
generated from the URL and username.

Usage:
    uv run agent_state_store.py --url https://example.com --username user --password pass
"""

import argparse
import asyncio
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from browser_use import ActionResult, Agent, Browser, ChatOpenAI, Controller
from browser_use.browser.session import BrowserSession
from browser_use.tools.registry.service import pyotp
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Directory to store saved browser states
BROWSER_STATES_DIR = Path(__file__).parent / "browser_states"
BROWSER_STATES_DIR.mkdir(exist_ok=True)


def generate_state_name(url: str, username: str) -> str:
    """Generate a state filename from URL and username."""
    # Extract domain from URL
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    # Clean domain and username to be filesystem-safe
    domain_clean = re.sub(r'[^\w\-.]', '_', domain)
    username_clean = re.sub(r'[^\w\-.]', '_', username)
    return f"{domain_clean}_{username_clean}"


class SaveBrowserStateParams(BaseModel):
    state_name: str


# Create controller with custom save action
controller = Controller()


@controller.action(
    "Save the current browser state (cookies, localStorage, sessionStorage) to disk",
    param_model=SaveBrowserStateParams
)
async def save_browser_state(params: SaveBrowserStateParams, browser_session: BrowserSession) -> str:
    """Save the current browser storage state to disk."""
    state_name = params.state_name
    state_path = BROWSER_STATES_DIR / f"{state_name}.json"
    
    try:
        # Capture cookies, localStorage, and sessionStorage using CDP
        storage_state = await browser_session._cdp_get_storage_state()
        
        cookies_count = len(storage_state.get('cookies', []))
        origins_count = len(storage_state.get('origins', []))
        
        # Save to file
        state_path.write_text(json.dumps(storage_state, indent=2))
        
        # Pause and wait for user input
        print(f"\n⏸️  Paused at line 68 - State saved to: {state_path}")
        input("Press Enter to continue...")
        
        return f"✓ Successfully saved browser state '{state_name}' to {state_path}\n  - {cookies_count} cookies\n  - {origins_count} origins with localStorage/sessionStorage"
    except Exception as e:
        return f"✗ Error saving browser state '{state_name}': {str(e)}"

@controller.action(description="""
    Get a valid TOTP code. 
    CRITICAL: Before generating new OTP codes, ALWAYS check your memory/history for previously generated codes. 
    OTP codes are valid for ~30 seconds - if you already generated codes recently and they are still valid, REUSE THEM. 
    Only generate new codes if: (1) no codes were generated yet in this session, (2) previous codes expired (more than 30 seconds ago), or (3) you received an explicit error that the code was rejected. 
    If you see the 2FA page and already have valid OTP codes in your memory from a previous tool call, USE THOSE CODES instead of generating new ones. 
    Generating codes multiple times when you already have valid codes will cause unnecessary loops. 
    Note: when deciding what steps to take, TOTP must at ALL COST be called as the single step instead of in a series. The reason is that the output of this call IS NEEEDED to perform the next step. Using templated string like {{OTP}} WILL NOT WORK. YOU NEED TO MAKE SURE TO CALL THIS TOOL ALONE BY ITSELF. 
    The output format is: "OTP code: {{code}} (for credential: {{prompt}})" - each line contains one OTP code with its associated credential context. When multiple codes are generated, match the code to the correct credential using the prompt context (e.g., email address) to identify which credential set it belongs to.
""")
async def generate_totp_code(OTP_SECRET: str) -> ActionResult:
    """Get a valid TOTP code."""
    try:
        # Generate OTP codes for all credentials with OTP URLs
        totp = pyotp.TOTP(OTP_SECRET)
        current_code = totp.at(time.time()+20)
        
        if not current_code:
            return ActionResult(
                extracted_content="Error: TOTP code is not generated",
                include_in_memory=True
            )
        
        return ActionResult(
            extracted_content=f"OTP code: {current_code}",
            include_in_memory=True
        )
    except Exception as e:
        return ActionResult(
            extracted_content=f"Error: {str(e)}",
            include_in_memory=True
        )

async def store_browser_state(
    url: str,
    username: str,
    password: str,
    headless: bool = False,
    max_steps: int = 20,
    otp_secret: str | None = None,
) -> None:
    """Log in to a website and save the browser state."""
    
    # Generate state name from URL and username
    state_name = generate_state_name(url, username)
    
    # Create browser
    browser = Browser(
        headless=headless,
        window_size={"width": 1280, "height": 800},
        # minimum_wait_page_load_time=2,
        # wait_between_actions=1,
        # wait_for_network_idle_page_load_time=2,
        paint_order_filtering=False,
    )
    
    # Use a capable model
    llm = ChatOpenAI(model="gpt-4o")
    
    # Task for the agent
    task = f"""
Go to {url} and log in with the following credentials:
- Username: {username}
- Password: {password}

If you need to enter a TOTP code, use the generate_totp_code tool with the following OTP secret: {otp_secret}
After successfully logging in and verifying you're authenticated:
1. Save the browser state with name "{state_name}"
2. Confirm the save was successful

Your goal is to capture the authenticated session state so it can be restored later.
"""

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        controller=controller,
        use_vision=True,
    )
    
    print("=" * 70)
    print("Browser State Storage Script")
    print("=" * 70)
    print(f"Target URL: {url}")
    print(f"Username: {username}")
    print(f"State name: {state_name}")
    print(f"Output directory: {BROWSER_STATES_DIR}")
    print("=" * 70)
    
    try:
        history = await agent.run(max_steps=max_steps)
        
        print("\n" + "-" * 70)
        print(f"Agent completed: {history.is_done()}")
        print(f"Success: {history.is_successful()}")
        print(f"Steps taken: {history.number_of_steps()}")
        print(f"Duration: {history.total_duration_seconds():.2f}s")
        
        if history.final_result():
            print(f"\nFinal Result:\n{history.final_result()}")
        
        if history.has_errors():
            print(f"\nErrors: {history.errors()}")
        
        # Verify the state file was created
        state_file = BROWSER_STATES_DIR / f"{state_name}.json"
        if state_file.exists():
            print("\n" + "=" * 70)
            print(f"✓ Browser state saved successfully: {state_file}")
            print(f"  File size: {state_file.stat().st_size} bytes")
            
            # Show a preview of what was saved
            state_data = json.loads(state_file.read_text())
            print(f"  Cookies: {len(state_data.get('cookies', []))}")
            print(f"  Origins: {len(state_data.get('origins', []))}")
        else:
            print("\n" + "=" * 70)
            print(f"✗ Warning: State file was not created at {state_file}")
            
    finally:
        await browser.stop()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Login and save browser state to JSON (filename auto-generated from URL and username)"
    )
    parser.add_argument(
        "--url",
        type=str,
        required=True,
        help="Target URL to log in to",
    )
    parser.add_argument(
        "--username",
        type=str,
        required=True,
        help="Username for login",
    )
    parser.add_argument(
        "--password",
        type=str,
        required=True,
        help="Password for login",
    )
    parser.add_argument(
        "--otp-secret",
        type=str,
        help="OTP secret for login",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=20,
        help="Maximum number of steps for the agent",
    )
    
    args = parser.parse_args()
    
    asyncio.run(
        store_browser_state(
            url=args.url,
            username=args.username,
            password=args.password,
            headless=args.headless,
            max_steps=args.max_steps,
            otp_secret=args.otp_secret,
        )
    )


if __name__ == "__main__":
    main()
