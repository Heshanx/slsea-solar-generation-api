from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30))  # admin | province | district
    # Jurisdiction scope: NULL/NULL for admin, province_id for province officers,
    # district_id for district officers.
    province_id: Mapped[int | None] = mapped_column(ForeignKey("provinces.id"))
    district_id: Mapped[int | None] = mapped_column(ForeignKey("districts.id"))