from sqlalchemy import Column, Integer, String
from db.base import Base


class User(Base):
    """Пользователь (для хранения лайков)."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
