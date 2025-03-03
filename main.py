from fastapi import FastAPI, Response, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field, field_validator
from pydantic_core import PydanticCustomError
from icecream import ic


app = FastAPI(
    title="Book Library App",
    description="Приложение для ШАД",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not Found!"}}
)


COUNTER = 0
all_books = dict()


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


@app.get("/", include_in_schema=False)
async def main():
    return "Hello World!"


@app.post("/books/", response_model=ReturnedBook)
async def create_book(book: IncomingBook):
    global new_book, COUNTER

    new_book = {
        "id": COUNTER,
        "title": book.title,
        "author": book.author,
        "year": book.year,
        "pages": book.pages
    }

    all_books[COUNTER] = new_book
    COUNTER += 1

    return ORJSONResponse({"book": new_book}, status_code=status.HTTP_201_CREATED)


@app.get("/books", response_model=ReturnedAllBooks)
async def get_books():
    return {"books": list(all_books.values())}


@app.get("/books/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int):
    book = all_books.get(book_id, None)

    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = all_books.pop(book_id, None)
    ic(deleted_book)

@app.put("/books/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book: ReturnedBook):
    print('________________________________________________________________')
    if _ := all_books[book_id]:
        tmp_book = {
            "id": book_id,
            "title": new_book.title,
            "author": new_book.author,
            "year": new_book.year,
            "pages": new_book.pages
        }
        all_books[book_id] = tmp_book

    return all_books[book_id]