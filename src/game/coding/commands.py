from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Type

from game.robot_game import RobotGame, RobotException
from game.exceptions import CompilerException


@dataclass
class CommandResults:
    should_terminate_program: bool
    should_jump_pc: bool
    next_pc: int | None = None
    error: str | None = None

    @staticmethod
    def default() -> 'CommandResults':
        return CommandResults(False, False, None, None)


class Command(ABC):
    pc: int

    def __init__(self, pc: int):
        self.pc = pc

    @abstractmethod
    def execute(self, game: RobotGame) -> CommandResults:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({self.pc}"


def is_robot_on_finish_zone(game: RobotGame) -> bool:
    return game.robot.current_position == game.board.finish_position


class MoveCommand(Command):
    x_direction: int
    y_direction: int

    def __init__(self, pc: int, x_direction: int, y_direction: int):
        super().__init__(pc)
        self.x_direction = x_direction
        self.y_direction = y_direction

    def execute(self, game: RobotGame) -> CommandResults:
        return self.move(game)

    def move(self, game: RobotGame) -> CommandResults:
        game.robot.move_in_direction(self.x_direction, self.y_direction)
        game.robot.update_sensors()
        try:
            game.robot.self_evaluate(self.pc)
        except RobotException as e:
            return CommandResults(True, False, None, str(e))
        game.robot_in_finish_zone = is_robot_on_finish_zone(game)
        return CommandResults.default()

    def __str__(self):
        return f"{self.__class__.__name__}({self.x_direction}, {self.y_direction}) at line {self.pc}"


class MoveUpCommand(MoveCommand):
    def __init__(self, pc: int):
        super().__init__(pc, 0, -1)


class MoveDownCommand(MoveCommand):
    def __init__(self, pc: int):
        super().__init__(pc, 0, 1)


class MoveLeftCommand(MoveCommand):
    def __init__(self, pc: int):
        super().__init__(pc, -1, 0)


class MoveRightCommand(MoveCommand):
    def __init__(self, pc: int):
        super().__init__(pc, 1, 0)


class PickUpCommand(Command):
    def execute(self, game: RobotGame) -> CommandResults:
        if game.robot.has_object:
            return CommandResults(
                True,
                False,
                None,
                "Robot tried to pick up an object while already holding one at line %s" % self.pc)

        if game.board.object_initial_position != game.robot.current_position:
            return CommandResults(
                True,
                False,
                None,
                "Robot tried to pick up an object from the wrong place and broke its arm at line %s" % self.pc)

        game.robot.has_object = True

        return CommandResults.default()


class DropCommand(Command):
    def execute(self, game: RobotGame) -> CommandResults:
        if not game.robot.has_object:
            return CommandResults(
                True,
                False,
                None,
                "Robot tried to drop an object while not holding one at line %s" % self.pc)

        game.robot.has_object = False
        if game.board.object_drop_zone_position == game.robot.current_position:
            game.object_in_drop_zone = True
        else:
            return CommandResults(
                True,
                False,
                None,
                "Robot tried to drop an object in the wrong place at line %s" % self.pc)

        return CommandResults.default()


class GoToCommand(Command):
    next_pc: int

    def __init__(self, pc: int, next_pc: int):
        super().__init__(pc)
        self.next_pc = next_pc

    def execute(self, game: RobotGame) -> CommandResults:
        return CommandResults(False, True, self.next_pc, None)

    def __str__(self):
        return f"{self.__class__.__name__}({self.next_pc}) at line {self.pc}"


class GoToIfSensorCommand(Command):
    next_pc: int
    sensor: str
    tile_type: str

    def __init__(self, pc: int, next_pc: int, sensor: str, tile_type: str):
        super().__init__(pc)
        self.next_pc = next_pc
        self.sensor = sensor
        self.tile_type = tile_type

    def execute(self, game: RobotGame) -> CommandResults:
        match self.sensor:
            case "UP":
                robot_sensor = game.robot.sensor_up
            case "DOWN":
                robot_sensor = game.robot.sensor_down
            case "LEFT":
                robot_sensor = game.robot.sensor_left
            case "RIGHT":
                robot_sensor = game.robot.sensor_right
            case _:
                raise CompilerException(
                    self.pc,
                    f"Unknown sensor {self.sensor}"
                )

        if robot_sensor.tile_type.string_value == self.tile_type:
            return CommandResults(False, True, self.next_pc, None)
        return CommandResults.default()

    def __str__(self):
        return f"{self.__class__.__name__}({self.next_pc}, {self.sensor} is {self.tile_type}) at line {self.pc}"


class NoOpCommand(Command):
    def execute(self, game: RobotGame) -> CommandResults:
        return CommandResults.default()


SUPPORTER_COMMANDS: dict[str, Type[Command]] = {
    "UP": MoveUpCommand,
    "RIGHT": MoveRightCommand,
    "LEFT": MoveLeftCommand,
    "DOWN": MoveDownCommand,
    "PICK_UP": PickUpCommand,
    "DROP": DropCommand,
    r"GOTO (\d+)": GoToCommand,
    r"GOTO (\d+) IF SENSOR [UP|RIGHT|DOWN|LEFT] IS [WALL|VOID|FLOOR|OBJECT|DROP_ZONE]": GoToIfSensorCommand,
    "NOOP": NoOpCommand,
}
