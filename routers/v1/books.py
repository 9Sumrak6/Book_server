from fastapi import Response, status, APIRouter
from fastapi.responses import ORJSONResponse
from icecream import ic


from schemas import IncomingBook, ReturnedBook, ReturnedAllBooks


all_books = dict()
COUNTER = 0

books_router = APIRouter(tags=["books"], prefix="/books")


@books_router.post("/", response_model=ReturnedBook)
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


@books_router.get("/", response_model=ReturnedAllBooks)
async def get_books():
    return {"books": list(all_books.values())}


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int):
    book = all_books.get(book_id, None)

    if book is not None:
        return book

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@books_router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    deleted_book = all_books.pop(book_id, None)
    ic(deleted_book)


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_book: ReturnedBook):
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