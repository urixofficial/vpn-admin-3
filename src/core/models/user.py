from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
	from .transaction import TransactionModel
	from .message import MessageModel
	from .awg import AwgRecordModel


class UserModel(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	name: Mapped[str] = mapped_column(String(32), unique=True)
	is_active: Mapped[bool] = mapped_column(default=True, server_default="1")
	balance: Mapped[int] = mapped_column(default=0, server_default="0")
	created_at: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())

	transactions: Mapped[list["TransactionModel"]] = relationship(
		back_populates="user",
		cascade="all, delete",
		passive_deletes=True,
	)
	messages: Mapped[list["MessageModel"]] = relationship(
		back_populates="user",
		cascade="all, delete",
		passive_deletes=True,
	)
	awg: Mapped[list["AwgRecordModel"]] = relationship(
		back_populates="user",
		cascade="all, delete",
		passive_deletes=True,
	)
