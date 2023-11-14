class GameException(Exception):
    pass


class CompilerException(Exception):
    def __init__(self, step: int, message: str):
        super().__init__(f"{message} on line {step}")


class RobotException(Exception):
    default_message = "We lost contact with the robot"

    def __init__(self, step: int, message: str = default_message):
        super().__init__(f"{message} after step {step}")


class NameForChallengeAlreadyExistsException(GameException):
    message = "Unable to create challenge %s: name already exists"

    def __init__(self, challenge_name: str):
        super().__init__(self.message % challenge_name)


class BoardException(GameException):
    pass


class UnknownTileValueException(BoardException):
    message = "Unable to create board for challenge %s: unknown tile value %s"

    def __init__(self, challenge_name: str, tile_value: str):
        super().__init__(self.message.format(challenge_name, tile_value))


class MissingStartPositionException(BoardException):
    message = "Unable to create board for challenge %s: no start position found"

    def __init__(self, challenge_name: str):
        super().__init__(self.message.format(challenge_name))
