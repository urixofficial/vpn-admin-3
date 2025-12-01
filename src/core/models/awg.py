from typing import TYPE_CHECKING

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
	from .user import UserModel


class AwgRecordModel(Base):
	__tablename__ = "awg"
	id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	ip: Mapped[str]
	mask: Mapped[int]
	public_key: Mapped[str]
	private_key: Mapped[str]
	created_at: Mapped[datetime] = mapped_column(default=datetime.now(), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), server_default=func.now())

	user: Mapped["UserModel"] = relationship(back_populates="awg")
