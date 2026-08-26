from typing import Any


def build_response(data: Any = None, message: str = "Success") -> dict:
    response = {"message": message}
    if data is not None:
        response["data"] = data
    return response
