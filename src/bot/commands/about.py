from discord.ext import commands
from ..robotbot import RobotBot


class About(commands.Cog):
    def __init__(self, bot: RobotBot):
        self.bot = bot

    @commands.command()
    async def about(self, ctx: commands.Context):
        """What is this game about?"""
        await ctx.send("## What is this game?\n"
                       "There is a robot somewhere in the moon performing tasks and they have asked you to program "
                       "their every action.\n"
                       "## How do I play?\n"
                       "The game works by someone creating a challenge for others to solve. The challenge is a map the "
                       "bot has to navigate in order to pick up an object and drop it at a specific location, then "
                       "go to the finishing position.\n"
                       "Players try to solve the challenge by writing a program for the robot to execute. The program "
                       "is a list of commands in a fictional programming language that the robot can understand.\n"
                       "## How do I write a program?\n"
                       "The programming language follows the format of ``<line_number> <instruction> // "
                       "<optional:comment>``."
                       "The line number is the order in which the robot will execute the command. The instruction is "
                       "the command the robot will execute. The comment is an optional comment that will be ignored.\n"
                       "## What commands are available?\n"
                       "```\n"
                       "1. UP\n"
                       "2. DOWN\n"
                       "3. LEFT\n"
                       "4. RIGHT\n"
                       "5. PICK_UP\n"
                       "6. DROP\n"
                       "7. GOTO <line_number>\n"
                       "8. GOTO <line_number> IF SENSOR [UP|RIGHT|DOWN|LEFT] IS [WALL|VOID|FLOOR|OBJECT|DROP_ZONE]\n"
                       "9. NOOP\n"
                       "```\n"
                       "Find available  commands with `>help`.\n")

    @commands.command()
    async def mapping(self, ctx: commands.Context):
        """How do you make maps?"""
        await ctx.send("## How do you create maps?\n"
                       "Maps are created by using the following characters:\n"
                       "```\n"
                       "0: the void of space\n"
                       "1: a wall\n"
                       "2: a floor tile\n"
                       "s: the starting position\n"
                       "f: the finishing position\n"
                       "o: the object to pick up\n"
                       "d: the drop zone\n"
                       "```\n"
                       "Just use the ``>add-challenge <name> <row1> <row2> <rowx>`` command to create a new map.\n"
                       )


async def setup(bot: RobotBot):
    await bot.add_cog(About(bot))
