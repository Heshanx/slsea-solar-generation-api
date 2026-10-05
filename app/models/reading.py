from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Reading(Base):
    __tablename__ = "readings"
    __table_args__ = (
        UniqueConstraint("installation_id", "recorded_at", name="uq_reading_installation_time"),
        Index("ix_readings_installation_time", "installation_id", "recorded_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    installation_id: Mapped[int] = mapped_column(ForeignKey("installations.id"))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    power_kw: Mapped[float | None] = mapped_column(Numeric(10, 3))
    energy_kwh: Mapped[float] = mapped_column(Numeric(12, 3))

    installation: Mapped["Installation"] = relationship(back_populates="readings")