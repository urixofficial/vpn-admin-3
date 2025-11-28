from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from core.config import settings


class Base(DeclarativeBase):
	__abstract__ = True

	metadata = MetaData(naming_convention=settings.db.naming_convention)
	# @declared_attr.directive
	# def __table_name__(cls) -> str:
	# 	return f"{cls.__name__.lower()}s"

	repr_cols_num = 2
	repr_cols = tuple()

	def __repr__(self):
		# cols = [f"{col}={getattr(self, col)}" for col in self.__table__.columns.keys()]
		cols = []
		for idx, col in enumerate(self.__table__.columns.keys()):
			if col in self.repr_cols or idx < self.repr_cols_num:
				cols.append(f"{col}={getattr(self, col)}")

		return f"<{self.__class__.__name__} {', '.join(cols)}>"
