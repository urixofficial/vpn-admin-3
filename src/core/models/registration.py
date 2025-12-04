from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from .base import Base


class TransactionModel(Base):
	__tablename__ = "registrations"
	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
	user_id: Mapped[int]
	username: Mapped[str]
	full_name: Mapped[str]
	created_at: Mapped[datetime] = mapped_column(default=datetime.now(), server_default=func.now())
