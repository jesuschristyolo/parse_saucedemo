from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.db_engine import Base
from sqlalchemy import String, ForeignKey
import datetime


class Positions(Base):
    __tablename__ = "positions"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[Optional[str]]
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete='CASCADE'))

    user: Mapped["Users"] = relationship("Users", back_populates="positions")


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    first_name: Mapped[Optional[str]] = mapped_column(String(50))
    last_name: Mapped[Optional[str]] = mapped_column(String(50))
    postal_code: Mapped[Optional[str]] = mapped_column(String(50))
    order_timestamp: Mapped[Optional[datetime.datetime]]

    positions: Mapped[List["Positions"]] = relationship(
        "Positions", back_populates="user")
