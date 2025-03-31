import pytest
from sqlalchemy import select
from src.models.seller import Seller
from src.models.books import Book
from fastapi import status
from icecream import ic


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    result_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED

    assert result_data == {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "id": result_data.get("id", None),
        "books": []
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller_1 = Seller(first_name="John", last_name="John", e_mail="john.doe123123123@example.com", password="lalala")
    seller_2 = Seller(first_name="Doe", last_name="Doe", e_mail="john.doe123123123@example.com", password="lalala")

    db_session.add_all([seller_1, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK
    result_data = response.json()

    assert (
        len(result_data) == 2
    )  # Опасный паттерн! Если в БД есть данные, то тест упадет

    seller_id_1, seller_id_2 = result_data[0].get("id", None), result_data[1].get("id", None)

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert result_data == [
            {
                "first_name": "John",
                "last_name": "John",
                "e_mail": "john.doe123123123@example.com",
                "id": seller_id_1,
                "books": []
            },
            {
                "first_name": "Doe",
                "last_name": "Doe",
                "e_mail": "john.doe123123123@example.com",
                "id": seller_id_2,
                "books": []
            },
        ]


# Тест на ручку получения одной книги
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
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

    response = await async_client.get(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_200_OK

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "books": [],
        "id": seller_id
    }


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    # Создаем книги вручную, а не через ручку, чтобы нам не попасться на ошибку которая
    # может случиться в POST ручке
    data = {
        "first_name": "John",
        "last_name": "John",
        "e_mail": "John@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    response = await async_client.put(
        f"/api/v1/sellers/{seller_id}",
        json={
            "first_name": "Doe",
            "last_name": "Doe",
            "e_mail": "Doe@example.com",
        }
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(Seller, seller_id)
    assert res.first_name == "Doe"
    assert res.last_name == "Doe"
    assert res.e_mail == "Doe@example.com"


# каскадное удаление продавцов и книг
@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
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

    response = await async_client.delete(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    await db_session.flush()

    all_books = await db_session.execute(select(Book))
    res = all_books.scalars().all()
    assert len(res) == 0

    all_sellers = await db_session.execute(select(Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0


@pytest.mark.asyncio
async def test_delete_seller_with_invalid_seller_id(db_session, async_client):
    data = {
        "first_name": "John",
        "last_name": "Doe",
        "e_mail": "john.doe123123123@example.com",
        "password": "lalala",
    }

    response = await async_client.post("/api/v1/sellers/", json=data)
    seller_id = response.json().pop("id", None)

    response = await async_client.delete(f"/api/v1/sellers/{seller_id + 1}")

    assert response.status_code == status.HTTP_404_NOT_FOUND