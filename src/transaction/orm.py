from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from src.core.orm import Base

class TransactionOrm(Base):
	__tablename__ = "transactions"
	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int]
	amount: Mapped[int]
	created_at: Mapped[datetime] = mapped_column(
		default=datetime.now(), server_default=func.now()
	)
	updated_at: Mapped[datetime] = mapped_column(
		default=datetime.now(), server_default=func.now()
	)