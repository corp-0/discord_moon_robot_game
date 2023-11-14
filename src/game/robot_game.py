from dataclasses import dataclass
from typing import Tuple

from discord.user import User

from game.board import Board
from game.exceptions import RobotException
from game.tile import Tile


@dataclass
class RobotEntity:
    board: Board
    current_position: Tuple[int, int]
    has_object: bool
    sensor_up: Tile | None
    sensor_down: Tile | None
    sensor_left: Tile | None
    sensor_right: Tile | None

    def __init__(self, board: Board):
        self.board = board
        self.current_position = board.start_position
        self.has_object = False
        self.sensor_up = None
        self.sensor_down = None
        self.sensor_left = None
        self.sensor_right = None

    def update_sensors(self):
        self.sensor_up = self.board.get_tile(self.current_position[0], self.current_position[1] - 1)
        self.sensor_down = self.board.get_tile(self.current_position[0], self.current_position[1] + 1)
        self.sensor_left = self.board.get_tile(self.current_position[0] - 1, self.current_position[1])
        self.sensor_right = self.board.get_tile(self.current_position[0] + 1, self.current_position[1])

    def self_evaluate(self, step: int):
        current_tile = self.board.get_tile(self.current_position[0], self.current_position[1])

        if current_tile.tile_type.string_value == "VOID":
            raise RobotException(step, "We lost contact with the robot. It fell into the void.")
        if current_tile.tile_type.string_value == "WALL":
            raise RobotException(step, "We lost contact with the robot. It hit a wall.")

    def move_in_direction(self, x_direction: int, y_direction: int):
        position_x = self.current_position[0]
        position_y = self.current_position[1]
        if x_direction != 0:
            position_x += x_direction
        if y_direction != 0:
            position_y += y_direction
        self.current_position = (position_x, position_y)


class RobotGame:
    discord_user_id: User
    board: Board
    robot: RobotEntity
    challenge_name: str
    object_in_drop_zone: bool = False
    robot_in_finish_zone: bool = False

    def __init__(self, discord_user_id: User, board: Board, robot: RobotEntity, challenge_name: str):
        self.discord_user_id = discord_user_id
        self.board = board
        self.robot = robot
        self.challenge_name = challenge_name

    @property
    def is_a_win(self) -> bool:
        return self.object_in_drop_zone and self.robot_in_finish_zone


class RobotChallenge:
    name: str
    players: list[User] = []
    challenge_string: str
    initial_map: str
    games: list[RobotGame] = []

    def __init__(self, name: str, challenge_string: str):
        self.name = name
        self.challenge_string = challenge_string
        self.initial_map = Board.from_string(name, challenge_string).get_emojis()

    async def add_player(self, player: User) -> RobotGame:
        self.players.append(player)
        board = Board.from_string(self.name, self.challenge_string)
        robot = RobotEntity(board)
        game = RobotGame(player, board, robot, self.name)
        self.games.append(game)
        return game

    async def remove_player(self, player: User):
        self.players.remove(player)
        self.games = [game for game in self.games if game.discord_user_id != player.id]
