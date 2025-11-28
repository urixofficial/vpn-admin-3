from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date

from .base import Base

if TYPE_CHECKING:
	from .transaction import TransactionModel
	from .message import MessageModel


class UserModel(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	name: Mapped[str] = mapped_column(String(32), unique=True)
	is_active: Mapped[bool] = mapped_column(default=True, server_default="TRUE")
	balance: Mapped[int] = mapped_column(default=0, server_default="0")
	billing_date: Mapped[date] = mapped_column(default=date.today(), server_default=func.current_date())
	created_at: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())

	transactions: Mapped[list["TransactionModel"]] = relationship(back_populates="user")
	messages: Mapped[list["MessageModel"]] = relationship(back_populates="user")
