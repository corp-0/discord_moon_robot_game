import discord
from cogwatch import watch
from discord.ext import commands

from game.robot_game import RobotChallenge


class RobotBot(commands.Bot):
    challenges: list[RobotChallenge] = []

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix=">", intents=intents)

    @watch(path='bot/commands', preload=True)
    async def on_ready(self):
        print("Robot is operational and ready to do  tasks!")

    async def on_message(self, message):
        if message.author.bot:
            return

        await self.process_commands(message)
