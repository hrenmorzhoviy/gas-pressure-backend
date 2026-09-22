from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from db.base import Base


class Like(Base):
    """
    Лайки — отношение many-to-many между пользователями и газами.
    Уникальное ограничение: один пользователь — один лайк на один газ.
    """
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gas_id = Column(Integer, ForeignKey("gases.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "gas_id", name="uq_user_gas_like"),
    )
