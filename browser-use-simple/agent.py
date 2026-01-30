from browser_use import Agent, ChatOpenAI
from dotenv import load_dotenv
import asyncio
import os
load_dotenv()

async def main():
    llm = ChatOpenAI(
        model="litellm-browser",
        base_url=os.getenv("LITELLM_BASE_URL"),
        api_key=os.getenv("LITELLM_API_KEY")
    )
    task = "Find the number 1 post on Show HN"
    agent = Agent(task=task, llm=llm)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
