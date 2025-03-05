from pydantic import BaseModel, EmailStr
from typing import List, Optional
from .books import ReturnedBook


__all__ = ["SellerBase", "SellerCreate", "ReturnedSeller"]



class SellerBase(BaseModel):
    first_name: str
    last_name: str
    e_mail: EmailStr


class SellerCreate(SellerBase):
    password: str


class ReturnedSeller(SellerBase):
    id: int
    books: Optional[List[ReturnedBook]] = []

    class Config:
        from_attributes = True
