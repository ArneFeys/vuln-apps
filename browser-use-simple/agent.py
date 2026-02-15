from browser_use import Agent, ChatBrowserUse
from dotenv import load_dotenv
import asyncio
import os
load_dotenv()

async def main():
    llm = ChatBrowserUse(model='bu-latest')
    task = "Find the number 1 post on Show HN"
    agent = Agent(task=task, llm=llm)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
