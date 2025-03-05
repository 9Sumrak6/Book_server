from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError


__all__ = ["IncomingBook", "ReturnedBook", "ReturnedAllBooks"]


class BaseBook(BaseModel):
    title: str
    author: str
    year: int


class IncomingBook(BaseBook):
    pages: int = Field(default=150, alias="pages_count")

    @field_validator("year")
    @staticmethod
    def validate_year(val: int):
        if val < 2020:
            raise PydanticCustomError("Validation error", "Year is too olad!")

        return val


class ReturnedBook(BaseBook):
    id: int
    pages: int


class ReturnedAllBooks(BaseModel):
    books: list[ReturnedBook]

