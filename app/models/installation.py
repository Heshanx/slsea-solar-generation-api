from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Installation(Base):
    __tablename__ = "installations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    capacity_kw: Mapped[float] = mapped_column(Numeric(10, 2))
    installation_type: Mapped[str] = mapped_column(String(30))  # rooftop | ground | floating
    status: Mapped[str] = mapped_column(String(20), default="active")
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6))
    commissioned_on: Mapped[date | None] = mapped_column(Date)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id"), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    district: Mapped["District"] = relationship(back_populates="installations")
    readings: Mapped[list["Reading"]] = relationship(back_populates="installation")