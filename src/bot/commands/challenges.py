from discord.ext import commands

from game.robot_game import RobotChallenge
from game.coding.program import Program, Parser
from ..robotbot import RobotBot


async def on_finished_execution(program: Program, ctx: commands.Context):
    print("Finished execution")
    if program.results.success:
        await ctx.send(
            f"🎉 Congratulations, {ctx.author.name}! 🌟\n"
            f"──────────────────────────\n"
            f"🔥 **Challenge Solved!** 🔥\n"
            f"👣 Steps: {program.results.steps}\n"
            f"⌛ Duration: {program.results.duration}\n"
            f"──────────────────────────"
        )
    else:
        await ctx.send(
            f"⚠️ Uh-oh, {ctx.author.name}, something didn't go as planned... ⚠️\n"
            f"──────────────────────────\n"
            f"🔍 **Challenge Attempt** 🔍\n"
            f"👣 Steps: {program.results.steps}\n"
            f"⌛ Duration: {program.results.duration}\n"
            f"❌ Error: {program.results.error}\n"
            f"──────────────────────────"
        )


class Challenges(commands.Cog):
    def __init__(self, bot: RobotBot):
        self.bot: RobotBot = bot

    @commands.command(name="add-challenge")
    async def add_challenge(self,
                            ctx: commands.Context,
                            name: str = commands.param(description="str: Name of the challenge"),
                            *challenge_string_rows: str
                            ):
        """Create a new challenge for others to play."""

        challenge_string = "\n".join(challenge_string_rows)
        await ctx.send(f"Adding challenge {name}")
        challenge = RobotChallenge(name, challenge_string)
        if name in [challenge.name for challenge in self.bot.challenges]:
            await ctx.send(f"Challenge {name} already exists")
            return
        self.bot.challenges.append(challenge)
        await ctx.send(f"Challenge {name}:\n{challenge.initial_map}")

    @commands.command(name="list-challenges")
    async def get_available_challenges(self, ctx: commands.Context):
        """What challenges are available?"""

        all_challenges: list[RobotChallenge] = self.bot.challenges
        challenges_message = "\n".join(
            [f"{idx}. {challenge.name}:\n{challenge.initial_map}" for idx, challenge in enumerate(all_challenges)])
        await ctx.send(f"Available challenges:\n{challenges_message}")

    @add_challenge.error
    async def add_challenge_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error.param.name + " is a required argument that is missing")
        else:
            await ctx.send("Unknown error")

    @commands.command(name="solve")
    async def solve_challenge(self, ctx: commands.Context, *, args):
        """Attempt to solve a challenge"""

        challenge_name = args.split("\n")[0].strip()
        code = "\n".join(args.split("\n")[1:]).strip()
        challenge = next((challenge for challenge in self.bot.challenges if challenge.name == challenge_name), None)
        if challenge is None:
            await ctx.send(f"Challenge {challenge_name} does not exist")
            return
        game = await challenge.add_player(ctx.author)
        await ctx.send(f"Trying {ctx.author.name}'s solution for {challenge_name}...")
        parser = Parser(code)
        try:
            parser.parse()
        except Exception as e:
            await ctx.send(f"❌ Something went wrong while parsing your code, {ctx.author.name}! ❌\n"
                           f"──────────────────────────"
                           f"```Error parsing code: {e}```")
            return
        program = Program(parser.parse(), ctx)
        print(f"Program: {program}")
        program.finished_execution_event.subscribe(on_finished_execution)
        await program.execute(game, ctx)


async def setup(bot: RobotBot):
    await bot.add_cog(Challenges(bot))
