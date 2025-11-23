from sqlalchemy import BigInteger, String, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date

from src.core.orm import Base


class UserOrm(Base):
	__tablename__ = "users"
	
	id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
	name: Mapped[str] = mapped_column(String(32))
	balance: Mapped[int] = mapped_column(default=0, server_default="0")
	billing_date: Mapped[date] = mapped_column(default=date.today(), server_default=func.current_date())
	created_at: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())
	updated_at: Mapped[datetime] = mapped_column(default=datetime.now, server_default=func.now())