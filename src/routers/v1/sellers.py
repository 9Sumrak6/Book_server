from typing import Annotated
from fastapi import APIRouter, Depends, Response, status, FastAPI, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import SellerBase, ReturnedSeller, SellerCreate
from src.models.seller import Seller
from src.config import get_async_session
from src.schemas import ReturnedBook


sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


# Регистрация продавца
@sellers_router.post("/", response_model=ReturnedSeller)
async def create_seller(seller: SellerCreate, session: DBSession):
    db_seller = Seller(**{
            "first_name": seller.first_name,
            "last_name": seller.last_name,
            "password": seller.password,
            "e_mail": seller.e_mail,
            "books": []
        })

    session.add(db_seller)
    await session.flush()

    return db_seller

# Получение списка всех продавцов
@sellers_router.get("/", response_model=list[ReturnedSeller])
async def get_sellers(session: DBSession):
    query = select(Seller).options(joinedload(Seller.books))
    result = await session.execute(query)
    sellers = result.unique().scalars().all()

    # Преобразуем продавцов в Pydantic модель
    return [
        ReturnedSeller(
            id=seller.id,
            first_name=seller.first_name,
            last_name=seller.last_name,
            e_mail=seller.e_mail,
            books=[
                ReturnedBook(
                    id=book.id,
                    author=book.author,
                    title=book.title,
                    pages_count=book.pages_count,
                    year=book.year,
                    seller_id=seller.id
                )
                for book in seller.books
            ]
        )
        for seller in sellers
    ]

# Получение данных о конкретном продавце
@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(joinedload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalars().first()

    if seller:
        return ReturnedSeller(
                id=seller.id,
                first_name=seller.first_name,
                last_name=seller.last_name,
                e_mail=seller.e_mail,
                books=[
                    ReturnedBook(
                        id=book.id,
                        author=book.author,
                        title=book.title,
                        pages_count=book.pages_count,
                        year=book.year,
                        seller_id=seller.id
                    )
                    for book in seller.books
                ]
            )

    return Response(status_code=status.HTTP_404_NOT_FOUND)


# Обновление данных о продавце
@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller: SellerBase, session: DBSession):
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = seller.first_name
        updated_seller.last_name = seller.last_name
        updated_seller.e_mail = seller.e_mail

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)  


# Удаление продавца и его книг
@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    deleted_seller = await session.get(Seller, seller_id)
    ic(deleted_seller)

    if deleted_seller:
        await session.delete(deleted_seller)

        return deleted_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)
