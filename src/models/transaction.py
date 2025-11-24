from typing import TYPE_CHECKING

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from src.models.base import Base

if TYPE_CHECKING:
	from src.models.user import UserOrm

class TransactionOrm(Base):
	__tablename__ = "transactions"
	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	amount: Mapped[int]
	created_at: Mapped[datetime] = mapped_column(
		default=datetime.now(), server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.now(), server_default=func.now()
	)

	user: Mapped["UserOrm"] = relationship(back_populates="transactions")