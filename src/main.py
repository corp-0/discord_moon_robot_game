import asyncio
import os

from bot.robotbot import RobotBot


async def main(bot_token: str):
    bot = RobotBot()
    await bot.start(bot_token)

if __name__ == "__main__":
    token = os.getenv("BOT_TOKEN")
    if token is None:
        print("Please set the BOT_TOKEN environment variable")
        quit(1)

    asyncio.run(main(token))
