from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from db.base import Base


class Gas(Base):
    """
    Модель газа (услуга).
    Статусы: published | draft | deleted (мягкое удаление через is_deleted).
    """
    __tablename__ = "gases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    # Поля по предметной области:
    molar_mass = Column(Float, nullable=True)   # молярная масса, г/моль
    density = Column(Float, nullable=True)       # плотность, кг/м³
    description = Column(String(1000), nullable=True)
    # Медиа (ключи и URL Minio)
    image_key = Column(String(255), nullable=False, default="")
    video_key = Column(String(255), nullable=False, default="")
    image_url = Column(String(512), nullable=False, default="")
    video_url = Column(String(512), nullable=False, default="")
    # Статус: published | draft (is_deleted = True → "deleted")
    status = Column(String(20), nullable=False, default="draft")
    is_deleted = Column(Boolean, default=False)  # мягкое удаление
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    published_at = Column(DateTime(timezone=True), nullable=True)
