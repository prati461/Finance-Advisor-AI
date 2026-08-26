from fastapi import status


class AppException(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundException(AppException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status.HTTP_404_NOT_FOUND, detail)


class ConflictException(AppException):
    def __init__(self, detail: str = "Conflict") -> None:
        super().__init__(status.HTTP_409_CONFLICT, detail)


class UnauthorizedException(AppException):
    def __init__(self, detail: str = "Unauthorized") -> None:
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail)
