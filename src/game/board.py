from dataclasses import dataclass

from game.exceptions import MissingStartPositionException, UnknownTileValueException
from game.tile import Tile, TILES
from typing import Tuple


@dataclass
class Board:
    start_position: Tuple[int, int] = None
    finish_position: Tuple[int, int] = None
    object_initial_position: Tuple[int, int] = None
    object_drop_zone_position: Tuple[int, int] = None
    tiles: list[list[Tile]] = None

    @staticmethod
    def from_string(challenge_name: str, challenge_string: str) -> 'Board':
        # Split the string into lines to represent rows
        rows = challenge_string.strip().split('\n')

        # Create a new Board instance
        board = Board()

        # Iterate over each row
        board.tiles = []
        for y, row in enumerate(rows):
            board_row = []

            # Iterate over each character in the row to represent tiles
            for x, char in enumerate(row):
                if char in TILES:
                    # Create a Tile instance using the character as a key in the TILES dictionary
                    tile_type = TILES[char]
                    tile = Tile(position_x=x, position_y=y, tile_type=tile_type)
                    board_row.append(tile)
                    if tile_type.string_value == "START":
                        board.start_position = (x, y)
                    elif tile_type.string_value == "FINISH":
                        board.finish_position = (x, y)
                    elif tile_type.string_value == "OBJECT":
                        board.object_initial_position = (x, y)
                    elif tile_type.string_value == "DROP_ZONE":
                        board.object_drop_zone_position = (x, y)
                else:
                    raise UnknownTileValueException(challenge_name, char)

            # Append the row of tiles to the board's tiles
            board.tiles.append(board_row)

        if board.start_position is None:
            raise MissingStartPositionException(challenge_name)

        return board

    def get_emojis(self) -> str:
        return "\n".join(["".join([tile.tile_type.emoji for tile in row]) for row in self.tiles])

    def get_tile(self, x: int, y: int) -> Tile | None:
        try:
            tile = self.tiles[y][x]
            return tile
        except IndexError:
            return None
