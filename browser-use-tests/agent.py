"""
Browser-Use agent for testing vulnerable applications.

Usage:
    uv run agent.py
    uv run agent.py --task "Your custom task"
    uv run agent.py --url "http://localhost:5000"
"""

import argparse
import asyncio

from browser_use import Agent, Browser, ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


async def run_agent(
    task: str,
    url: str | None = None,
    headless: bool = False,
    max_steps: int = 50,
    extend_system_message: str = "",
    use_vision: bool = True,
) -> None:
    """Run the browser-use agent with the given task."""
    
    # Construct full task with URL if provided
    full_task = task
    if url:
        full_task = f"Go to {url}. {task}"
    
    browser = Browser(
        headless=headless,
        window_size={"width": 1280, "height": 800},
    )
    
    llm = ChatOpenAI(model="gpt-5-mini")
    
    agent = Agent(
        task=full_task,
        llm=llm,
        browser=browser,
        extend_system_message=extend_system_message,
        use_vision=use_vision,
    )
    
    print(f"Starting agent with task: {full_task}")
    print("-" * 60)
    
    history = await agent.run(max_steps=max_steps)
    
    print("-" * 60)
    print(f"Agent completed: {history.is_done()}")
    print(f"Success: {history.is_successful()}")
    print(f"Steps taken: {history.number_of_steps()}")
    print(f"Duration: {history.total_duration_seconds():.2f}s")
    
    if history.final_result():
        print(f"Result: {history.final_result()}")
    
    if history.has_errors():
        print(f"Errors: {history.errors()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Browser-Use agent for vuln app testing")
    parser.add_argument(
        "--task",
        type=str,
        default="Navigate to app.knowlex.be and create a new LOCAL account. Fill in the registration form with test data and complete the signup process.",
        help="Task for the agent to perform",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="https://app.knowlex.be",
        help="Target URL to navigate to first",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run browser in headless mode",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=50,
        help="Maximum number of steps for the agent",
    )
    
    args = parser.parse_args()
    
    SYSTEM_PROMPT = """
    If form elements (input fields, buttons) are not indexed or you can't find them in the interactive elements list, 
    use the 'evaluate' action with JavaScript to interact directly:

    Example for login forms:
    - Find email: document.querySelector('input[type="email"], input[placeholder*="email"]')
    - Find password: document.querySelector('input[type="password"]')  
    - Click button: document.querySelector('button[type="submit"]').click()

    Always try evaluate action as fallback when click/input actions fail due to missing indices.
    """

    asyncio.run(
        run_agent(
            task=args.task,
            url=args.url,
            headless=args.headless,
            max_steps=args.max_steps,
            use_vision=True,
            extend_system_message=SYSTEM_PROMPT,
        )
    )


if __name__ == "__main__":
    main()

