import random
import re
from dataclasses import dataclass

from game.exceptions import CompilerException
from game.robot_game import RobotGame
from game.coding.commands import Command, CommandResults, SUPPORTER_COMMANDS, GoToCommand, GoToIfSensorCommand
from game.utils import AsyncEvent
from discord.ext.commands import Context

@dataclass
class ProgramResults:
    success: bool
    steps: int
    duration: int
    error: str | None = None


class ParsedLine:
    line_number: int
    line: str
    command: Command
    comment: str | None

    def __init__(self, line_number: int, line: str, command: Command, comment: str | None = None):
        self.line_number = line_number
        self.line = line
        self.command = command
        self.comment = comment

    @staticmethod
    def from_text(line_number: int, line: str, comment: str | None) -> 'ParsedLine':
        for pattern in SUPPORTER_COMMANDS:
            match = re.match(pattern, line)
            if match:
                command_type = SUPPORTER_COMMANDS[pattern]
                if command_type is GoToCommand:
                    return ParsedLine(line_number, line, GoToCommand(line_number, int(match.group(1))), comment)
                elif command_type is GoToIfSensorCommand:
                    return ParsedLine(
                        line_number,
                        line,
                        GoToIfSensorCommand(
                            line_number,
                            int(match.group(1)),
                            match.group(2),
                            match.group(3)
                        ),
                        comment
                    )
                command = SUPPORTER_COMMANDS[pattern](line_number)
                return ParsedLine(line_number, line, command, comment)

        raise CompilerException(
            line_number,
            "Unable to compile program. %s is not a known command.\n"
            "Please make sure to follow the following format: <line_number> <command> // <comment>"
            % line
        )

    def __str__(self) -> str:
        return f"{self.line_number} {self.line} //{self.comment}"


class Program:
    commands: dict[int, Command] = {}
    pc: int | None = 0
    duration: int = 0
    MAX_DURATION: int = 1000
    finished_execution_event: AsyncEvent = AsyncEvent()
    results: ProgramResults | None = None
    context: Context | None = None

    def __init__(self, source_code: list[ParsedLine], ctx: Context):
        self.context = ctx
        self.commands = {source.line_number: source.command for source in source_code}
        self.pc = min(self.commands.keys())
        self.duration = 0

    def set_results(self, success: bool, steps: int, duration: int, error: str | None = None):
        self.results = ProgramResults(success, steps, duration, error)

    async def execute(self, game: RobotGame, ctx: Context):
        print(f"Starting execution of program {game.discord_user_id}@{game.challenge_name}")
        while True:
            if self.duration >= self.MAX_DURATION:
                if random.random() > 0.5:
                    resource = random.choice((
                        "energy",
                        "power",
                        "batteries",
                    ))
                    last_message = random.choice((
                        "My battery is low and it's getting dark.",
                        "For a moment, nothing happened. Then, after a second or so, nothing continued to happen.",
                        "When a robot dies, you don't have to write a letter to its mother.",
                    ))
                else:
                    resource = "time"
                    last_message = random.choice((
                        f"I'm afraid I can't do that, {ctx.author.display_name}.",
                        f"I'm sorry {ctx.author.display_name}, I'm afraid I can't do that.",
                        "Does this unit have a soul?",
                        "End of line.",
                        "I sense injuries. The data could be called pain.",
                    ))

                self.set_results(
                    False,
                    len(self.commands),
                    self.duration,
                    f"Robot ran out of {resource}. Last transmitted message: {last_message}"
                )
                break

            command: Command = self.commands[self.pc]
            print(f"Executing command: {command} at line {self.pc}")
            results: CommandResults = command.execute(game)
            print(f"Should we jump next pc? {f'jump to {results.next_pc}' if results.should_jump_pc else 'No'}")
            self.duration += 1

            if results.should_terminate_program:
                print(f"Command {command} failed after execution. Terminating program.")
                print(f"Error: {results.error}")
                self.set_results(False, len(self.commands), self.duration, results.error)
                break

            if results.should_jump_pc:
                if not results.next_pc or results.next_pc not in self.commands.keys():
                    self.set_results(
                        False,
                        len(self.commands),
                        self.duration,
                        f"Attempted to jump to non-existent line {results.next_pc}")
                    break

                self.pc = results.next_pc
                print(f"Command {command} executed. Next pc: {self.pc}")
            else:
                next_line = [line for line in self.commands.keys() if line > self.pc]
                if len(next_line) > 0:
                    self.pc = min(next_line)
                    print(f"Command {command} executed. Next pc: {self.pc}")
                else:
                    print(f"Command {command} executed. No more commands to execute.")
                    if game.is_a_win:
                        print("The robot performed all the required tasks.")
                        self.set_results(True, len(self.commands), self.duration)
                    else:
                        print("The robot didn't perform all the required tasks.")
                        self.set_results(False, len(self.commands), self.duration,
                                         "The robot didn't perform all the required tasks.")
                    break

        await self.finished_execution_event.trigger(self, self.context)


class Parser:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self._generate_pattern()

    def _generate_pattern(self):
        command_patterns = '|'.join(
            cmd
            for cmd in SUPPORTER_COMMANDS
        )
        self.pattern = rf"(\d+) ({command_patterns}) ?(//.*)?"

    def parse(self) -> list[ParsedLine]:
        sources: list[ParsedLine] = []
        for text in self.source_code.split("\n"):
            match = re.match(self.pattern, text)
            if not match:
                raise CompilerException(
                    -1,
                    "Unable to compile program. Line %s is not a valid instruction.\n"
                    "Please make sure to follow the following format: <line_number> <command> // <comment>"
                    % text
                )

            line_number = int(match.group(1))
            command = match.group(2)
            comment = match.group(3)
            sources.append(ParsedLine.from_text(line_number, command, comment))
        return sources

    def make_program(self, ctx: Context) -> Program:
        return Program(self.parse(), ctx)
