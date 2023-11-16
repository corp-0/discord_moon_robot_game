from discord.ext import commands
from ..robotbot import RobotBot


class About(commands.Cog):
    @commands.command()
    async def about(self, ctx: commands.Context):
        """What is this game about?"""

        await ctx.send(
            f"""
## What is this game?
There is a robot somewhere on the moon performing tasks and they have asked you to program their every action.

## How do I play?
The game works by someone creating a challenge for others to solve. The challenge is a map the bot has to navigate in \
order to pick up an object and drop it at a specific location, then go to the finishing position.
Players try to solve the challenge by writing a program for the robot to execute. The program is a list of commands in \
a fictional programming language that the robot can understand.

## How do I write a program?
Each line consists of: `line_number instruction // comment`. For example: `10 RIGHT`
The line number is the order in which the robot will execute the command. The instruction is the command to run. \
Comments are ignored.

## What commands are available?
```
1. UP
2. DOWN
3. LEFT
4. RIGHT
5. PICK_UP
6. DROP
7. GOTO <line_number>
8. GOTO <line_number> IF SENSOR [UP|RIGHT|DOWN|LEFT] IS [WALL|VOID|FLOOR|OBJECT|DROP_ZONE]
9. NOOP
``` Find available  commands with `{ctx.prefix}help`.
"""
        )

    @commands.command()
    async def mapping(self, ctx: commands.Context):
        """How do you make maps?"""

        await ctx.send(
            f"""
## How do you create maps?
Maps are created by using the following characters:
```
0: the void of space
1: a wall
2: a floor tile
s: the starting position
f: the finishing position
o: the object to pick up
d: the drop zone
```
Just use the `{ctx.prefix}add-challenge <name> <row1> <row2> <rowx>` command to create a new map.
"""
        )


async def setup(bot: RobotBot):
    await bot.add_cog(About())
