from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    message: str = ""
    data: Optional[T] = None


def success(data: any = None, message: str = "") -> dict:
    return {"code": 0, "message": message, "data": data}


def error(message: str, code: int = 1, data: any = None) -> dict:
    return {"code": code, "message": message, "data": data}
