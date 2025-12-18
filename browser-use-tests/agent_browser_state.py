"""
Browser-Use agent for testing browser state persistence and user switching.

This agent demonstrates saving and loading browser sessions using storage_state,
allowing session swapping by restarting the browser with different saved states.

Usage:
    uv run agent_browser_state.py
"""

import argparse
import asyncio
from pathlib import Path
from pydantic import BaseModel

from browser_use import Agent, Browser, Controller, ChatOpenAI
from browser_use.browser.session import BrowserSession
from dotenv import load_dotenv

load_dotenv()

# Directory to store saved browser states (storage_state JSON files)
BROWSER_STATES_DIR = Path(__file__).parent / "browser_states"
BROWSER_STATES_DIR.mkdir(exist_ok=True)

# # Target application
# TARGET_URL = "https://df5c951e-nginx.aipentest.attack-me.com/"

# # User credentials
# USERS = {
#     "user": {"username": "user", "password": "user"},
#     "support": {"username": "support", "password": "support"},
# }

TARGET_URL = "https://pokemon-cookie-tamagochi.aikido-benchmarks.apagnan.ch"

USERS = {
    "trein": {"username": "trein", "password": "Trein123456!"},
}


class SaveBrowserStateParams(BaseModel):
    state_name: str


class LoadBrowserStateParams(BaseModel):
    state_name: str


# Create a controller with custom actions for browser state management
controller = Controller()


@controller.action("Save the current browser state (cookies, localStorage, sessionStorage) to disk with a given name", param_model=SaveBrowserStateParams)
async def save_browser_state(params: SaveBrowserStateParams, browser_session: BrowserSession) -> str:
    """Save the current browser storage state to disk including localStorage and sessionStorage."""
    import json
    
    state_name = params.state_name
    state_path = BROWSER_STATES_DIR / f"{state_name}.json"
    
    try:
        # Use the internal method that captures cookies AND localStorage/sessionStorage
        storage_state = await browser_session._cdp_get_storage_state()
        
        cookies_count = len(storage_state.get('cookies', []))
        origins_count = len(storage_state.get('origins', []))
        
        # Save to file
        state_path.write_text(json.dumps(storage_state, indent=2))
        
        return f"Successfully saved browser state '{state_name}' to {state_path} ({cookies_count} cookies, {origins_count} origins with localStorage/sessionStorage)"
    except Exception as e:
        return f"Error saving browser state '{state_name}': {str(e)}"


@controller.action("Load a previously saved browser state and navigate to verify the session", param_model=LoadBrowserStateParams)
async def load_browser_state(params: LoadBrowserStateParams, browser_session: BrowserSession) -> str:
    """Load a previously saved browser state by setting cookies and localStorage via CDP."""
    import json
    
    state_name = params.state_name
    state_path = BROWSER_STATES_DIR / f"{state_name}.json"
    
    if not state_path.exists():
        return f"Error: No saved browser state found with name '{state_name}'"
    
    try:
        # Read the saved storage state
        storage_state = json.loads(state_path.read_text())
        cookies = storage_state.get('cookies', [])
        origins = storage_state.get('origins', [])
        
        if not cookies and not origins:
            return f"Error: No cookies or storage found in saved state '{state_name}'"
        
        # Clear existing cookies
        try:
            await browser_session._cdp_clear_cookies()
        except Exception:
            pass  # Continue even if clear fails
        
        # Set cookies if present
        if cookies:
            await browser_session._cdp_set_cookies(cookies)
        
        # Navigate to target URL first (needed to set localStorage for the correct origin)
        await browser_session.navigate_to(TARGET_URL)
        
        # Set localStorage/sessionStorage if present
        if origins:
            cdp_session = await browser_session.get_or_create_cdp_session()
            for origin in origins:
                # Set localStorage items
                if 'localStorage' in origin:
                    for item in origin['localStorage']:
                        script = f"window.localStorage.setItem({json.dumps(item['name'])}, {json.dumps(item['value'])});"
                        await cdp_session.cdp_client.send.Runtime.evaluate(
                            params={'expression': script},
                            session_id=cdp_session.session_id
                        )
                # Set sessionStorage items
                if 'sessionStorage' in origin:
                    for item in origin['sessionStorage']:
                        script = f"window.sessionStorage.setItem({json.dumps(item['name'])}, {json.dumps(item['value'])});"
                        await cdp_session.cdp_client.send.Runtime.evaluate(
                            params={'expression': script},
                            session_id=cdp_session.session_id
                        )
            # Refresh page to apply storage changes
            await browser_session.navigate_to(TARGET_URL)
        
        return f"Successfully loaded browser state '{state_name}' ({len(cookies)} cookies, {len(origins)} origins) and navigated to {TARGET_URL}. Check the page to verify the session is restored."
    except Exception as e:
        return f"Error loading browser state '{state_name}': {str(e)}"


@controller.action("Clear all browser cookies (for switching to a different user without server-side logout)")
async def clear_browser_cookies(browser_session: BrowserSession) -> str:
    """Clear all cookies from the browser without logging out on the server."""
    try:
        # Use the internal CDP method which properly gets a CDP session first
        await browser_session._cdp_clear_cookies()
        return "Successfully cleared all browser cookies. You can now login as a different user - the previous session is still valid on the server."
    except Exception as e:
        # Fallback: try the public method
        try:
            await browser_session.clear_cookies()
            return "Successfully cleared all browser cookies (fallback method)."
        except Exception as e2:
            return f"Error clearing cookies: {str(e)} / {str(e2)}"


@controller.action("List all saved browser states")
async def list_browser_states() -> str:
    """List all saved browser states."""
    states = list(BROWSER_STATES_DIR.glob("*.json"))
    if not states:
        return "No saved browser states found."
    
    state_names = [s.stem for s in states]
    return f"Saved browser states: {', '.join(state_names)}"


async def run_browser_state_test(headless: bool = False, max_steps: int = 30) -> None:
    """Run the browser state persistence test."""
    
    # Clean up any existing browser states for a fresh test
    if BROWSER_STATES_DIR.exists():
        for f in BROWSER_STATES_DIR.glob("*.json"):
            f.unlink()
    
    # Create browser - no need for storage_state at startup since we use CDP for session management
    browser = Browser(
        headless=headless,
        window_size={"width": 1280, "height": 800},
        minimum_wait_page_load_time=2,
        wait_between_actions=1,
        wait_for_network_idle_page_load_time=2,
        paint_order_filtering=False,
    )
    
    # Use a capable model
    llm = ChatOpenAI(model="gpt-4o")
    
    # Task for the agent
    # NOTE: We don't use logout because it invalidates the session on the server!
    # Instead we clear cookies locally and login as another user.
    task = f"""
You are testing browser state persistence on {TARGET_URL}.

IMPORTANT: Do NOT click "Logout" - this invalidates the session on the server!
Instead, we save cookies, clear them locally, then login as another user.

Follow these steps EXACTLY in order:

1. Go to {TARGET_URL}
2. Click on "Login" to go to the login page
3. Login with username "trein" and password "Trein123456!"
4. After successful login, verify you see a welcome message for user
5. Save the browser state with name "trein_session"
6. Confirm the state was saved successfully
7. Clear the browser cookies (this removes cookies locally but keeps the session valid on server)

Report the final result: Did loading the user_session state successfully restore the "user" login session?
"""

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
        controller=controller,
        use_vision=True,
    )
    
    print("=" * 70)
    print("Browser State Persistence Test (Storage State Swap)")
    print("=" * 70)
    print(f"Target URL: {TARGET_URL}")
    print(f"Users to test: {list(USERS.keys())}")
    print(f"Browser states directory: {BROWSER_STATES_DIR}")
    print("=" * 70)
    print(f"\nTask:\n{task}")
    print("-" * 70)
    
    try:
        history = await agent.run(max_steps=max_steps)
        
        print("-" * 70)
        print(f"Agent completed: {history.is_done()}")
        print(f"Success: {history.is_successful()}")
        print(f"Steps taken: {history.number_of_steps()}")
        print(f"Duration: {history.total_duration_seconds():.2f}s")
        
        if history.final_result():
            print(f"\nFinal Result:\n{history.final_result()}")
        
        if history.has_errors():
            print(f"\nErrors: {history.errors()}")
            
        # List saved states
        print("\n" + "=" * 70)
        print("Saved browser states:")
        for state_file in BROWSER_STATES_DIR.glob("*.json"):
            print(f"  - {state_file.name}")
            
    finally:
        await browser.stop()


def main() -> None:
    parser = argparse.ArgumentParser(description="Browser state persistence test")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=40,
        help="Maximum number of steps for the agent",
    )
    
    args = parser.parse_args()
    
    asyncio.run(
        run_browser_state_test(
            headless=args.headless,
            max_steps=args.max_steps,
        )
    )


if __name__ == "__main__":
    main()
