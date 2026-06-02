from typing import TYPE_CHECKING

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from .base import Base

if TYPE_CHECKING:
	from .user import UserModel


class AwgRecordModel(Base):
	__tablename__: str = "awg"

	id: Mapped[int] = mapped_column(primary_key=True)
	ip: Mapped[str] = mapped_column(unique=True)
	mask: Mapped[int] = mapped_column()
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	public_key: Mapped[str] = mapped_column()
	private_key: Mapped[str] = mapped_column()
	created_at: Mapped[datetime] = mapped_column(
		default=datetime.now(),
		server_default=func.now(),
	)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.now(),
		onupdate=datetime.now(),
		server_default=func.now(),
		server_onupdate=func.now(),
	)

	user: Mapped["UserModel"] = relationship(back_populates="awg")
