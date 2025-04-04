import pytest
from sqlalchemy import select
from src.models.books import Book
from fastapi import status
from icecream import ic


# Тест на ручку создающую книгу
@pytest.mark.asyncio
async def test_create_book(async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED
    seller_id = response.json().pop("id", None)

    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages_count": 300,
        "year": 2025,
        "seller_id": seller_id,
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    resp_book_id = result_data.pop("id", None)
    assert resp_book_id, "Book id not returned from endpoint"

    assert result_data == {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages_count": 300,
        "year": 2025,
        "seller_id": seller_id,
    }


@pytest.mark.asyncio
async def test_create_book_with_old_year(async_client):
    data = {
        "title": "Clean Architecture",
        "author": "Robert Martin",
        "pages_count": 300,
        "year": 1986,
    }
    response = await async_client.post("/api/v1/books/", json=data)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# Тест на ручку получения списка книг
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages_count=104, seller_id=seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages_count=104, seller_id=seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/books/")

    assert response.status_code == status.HTTP_200_OK

    assert (
        len(response.json()["books"]) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "books": [
            {
                "title": "Eugeny Onegin",
                "author": "Pushkin",
                "year": 2001,
                "id": book.id,
                "pages_count": 104,
                "seller_id": seller_id,
            },
            {
                "title": "Mziri",
                "author": "Lermontov",
                "year": 1997,
                "id": book_2.id,
                "pages_count": 104,
                "seller_id": seller_id,
            },
        ]
    }


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages_count=104, seller_id=seller_id)
    book_2 = Book(author="Lermontov", title="Mziri", year=1997, pages_count=104, seller_id=seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "title": "Eugeny Onegin",
        "author": "Pushkin",
        "year": 2001,
        "pages_count": 104,
        "id": book.id,
        "seller_id": seller_id,
    }


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_book(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    book = Book(author="Pushkin", title="Eugeny Onegin", year=2001, pages_count=104, seller_id=seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/books/{book.id}",
        json={
            "title": "Mziri",
            "author": "Lermontov",
            "pages_count": 100,
            "year": 2007,
            "id": book.id,
            "seller_id": seller_id,
        },
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Book, book.id)
    assert res.title == "Mziri"
    assert res.author == "Lermontov"
    assert res.pages_count == 100
    assert res.year == 2007
    assert res.id == book.id
    assert res.seller_id == seller_id


@pytest.mark.asyncio
async def test_delete_book(db_session, async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    book = Book(author="Lermontov", title="Mtziri", pages_count=510, year=2024, seller_id=seller_id)

    db_session.add(book)
    await db_session.flush()
    ic(book.id)

    response = await async_client.delete(f"/api/v1/books/{book.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()
    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()

    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_book_with_invalid_book_id(db_session, async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    book = Book(author="Lermontov", title="Mtziri", pages_count=510, year=2024, seller_id=seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/books/{book.id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND