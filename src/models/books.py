from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel
from .seller import Seller


class Book(BaseModel):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int]
    pages_count: Mapped[int]
    seller_id: Mapped[int] = mapped_column(Integer, ForeignKey("sellers.id"), nullable=False)

    seller: Mapped["Seller"] = relationship("Seller", back_populates="books")
