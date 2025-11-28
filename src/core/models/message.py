from typing import TYPE_CHECKING

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from core.schemas.message import MessageStatus

from .base import Base

if TYPE_CHECKING:
	from .user import UserModel


class MessageModel(Base):
	__tablename__ = "messages"
	id: Mapped[int] = mapped_column(primary_key=True)
	chat_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	text: Mapped[int]
	status: Mapped[MessageStatus] = mapped_column(
		default=MessageStatus.PENDING, server_default=MessageStatus.PENDING.value
	)
	created_at: Mapped[datetime] = mapped_column(default=datetime.now(), server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(default=datetime.now(), server_default=func.now())

	user: Mapped["UserModel"] = relationship(back_populates="messages")
