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
    executed_lines: int
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
    executed_lines_amount: int = 0
    MAX_AMOUNT_OF_LINES: int = 1000
    finished_execution_event: AsyncEvent = AsyncEvent()
    results: ProgramResults | None = None
    context: Context | None = None

    def __init__(self, source_code: list[ParsedLine], ctx: Context):
        self.context = ctx
        self.commands = {source.line_number: source.command for source in source_code}
        self.pc = min(self.commands.keys())
        self.executed_lines_amount = 0

    def set_results(self, success: bool, steps: int, executed_lines: int, error: str | None = None):
        self.results = ProgramResults(success, steps, executed_lines, error)

    async def execute(self, game: RobotGame):
        print(f"Starting execution of program {game.discord_user_id}@{game.challenge_name}")
        while True:
            if self.executed_lines_amount >= self.MAX_AMOUNT_OF_LINES:
                self.set_results(
                    False,
                    len(self.commands),
                    self.executed_lines_amount,
                    "Robot ran out of memory and exploded."
                )
                break

            command: Command = self.commands[self.pc]
            print(f"Executing command: {command} at line {self.pc}")
            results: CommandResults = command.execute(game)
            print(f"Should we jump next pc? {f'jump to {results.next_pc}' if results.should_jump_pc else 'No'}")
            self.executed_lines_amount += 1

            if results.should_terminate_program:
                print(f"Command {command} failed after execution. Terminating program.")
                print(f"Error: {results.error}")
                self.set_results(False, len(self.commands), self.executed_lines_amount, results.error)
                break

            if results.should_jump_pc:
                if not results.next_pc or results.next_pc not in self.commands.keys():
                    self.set_results(
                        False,
                        len(self.commands),
                        self.executed_lines_amount,
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
                        self.set_results(True, len(self.commands), self.executed_lines_amount)
                    else:
                        print("The robot didn't perform all the required tasks.")
                        self.set_results(False, len(self.commands), self.executed_lines_amount,
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
