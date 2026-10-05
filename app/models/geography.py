from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Province(Base):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    districts: Mapped[list["District"]] = relationship(back_populates="province")


class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    province_id: Mapped[int] = mapped_column(ForeignKey("provinces.id"), index=True)

    province: Mapped[Province] = relationship(back_populates="districts")
    installations: Mapped[list["Installation"]] = relationship(back_populates="district")