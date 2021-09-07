class SkrimAPIException(Exception):
    """Base exception for Nexus League.
    """

    def __init__(self, msg: str = "Internal error", status_code: int = 500,
                 *args: object) -> None:

        self.msg = msg
        self.status_code = status_code

        super().__init__(*args)


class InvalidToken(SkrimAPIException):
    def __init__(self, msg: str = "Invalid token", status_code: int = 400,
                 *args: object) -> None:
        super().__init__(msg=msg, status_code=status_code, *args)
