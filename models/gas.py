from sqlalchemy import Column, Integer, String, Float, Boolean
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
    molar_mass = Column(Float, nullable=False)   # молярная масса, г/моль
    density = Column(Float, nullable=False)       # плотность, кг/м³
    description = Column(String(1000), nullable=False)
    # Медиа (ключи и URL Minio)
    image_key = Column(String(255), nullable=False, default="")
    video_key = Column(String(255), nullable=False, default="")
    image_url = Column(String(512), nullable=False, default="")
    video_url = Column(String(512), nullable=False, default="")
    # Статус: published | draft (is_deleted = True → "deleted")
    status = Column(String(20), nullable=False, default="draft")
    is_deleted = Column(Boolean, default=False)  # мягкое удаление
