from typing import Dict


class TileType:
    string_value: str
    emoji: str

    def __init__(self, string_value: str, emoji: str):
        self.string_value = string_value
        self.emoji = emoji

    def __str__(self):
        return self.string_value

    def __repr__(self):
        return self.string_value


TILES: Dict[str, TileType] = {
    "0": TileType("VOID", "🕳️"),
    "1": TileType("WALL", "🟦"),
    "2": TileType("FLOOR", "⬜"),
    "r": TileType("ROBOT", "🤖"),
    "s": TileType("START", "🤖"),
    "f": TileType("FINISH", "🏁"),
    "o": TileType("OBJECT", "📦"),
    "d": TileType("DROP_ZONE", "🎯"),
}


class Tile:
    position_x: int
    position_y: int
    tile_type: TileType

    def __init__(self, position_x: int, position_y: int, tile_type: TileType):
        self.position_x = position_x
        self.position_y = position_y
        self.tile_type = tile_type

    def to_coordinates(self):
        return tuple([self.position_x, self.position_y])

    def __str__(self):
        return f"Tile({self.position_x}, {self.position_y}, {self.tile_type})"

    def __repr__(self):
        return f"Tile({self.position_x}, {self.position_y}, {self.tile_type})"