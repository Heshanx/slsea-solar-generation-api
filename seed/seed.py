"""Deterministic seeder: same data on every run.

Run from the repo root:  python -m seed.seed
WARNING: wipes and reloads all tables (development only).
"""
import math
import random
from datetime import date, datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy import insert, text

from app.core.db import SessionLocal
from app.models import District, Installation, Province, Reading, User

SEED = 42
LK = timezone(timedelta(hours=5, minutes=30))  # Sri Lanka time
START = datetime(2026, 9, 15, tzinfo=LK)       # fixed window, not "now"
DAYS = 20

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# province -> [(district, lat, lng), ...]  (coordinates are approximate)
GEOGRAPHY = {
    "Western": [("Colombo", 6.93, 79.86), ("Gampaha", 7.09, 80.00), ("Kalutara", 6.58, 79.96)],
    "Central": [("Kandy", 7.29, 80.63), ("Matale", 7.47, 80.62), ("Nuwara Eliya", 6.97, 80.77)],
    "Southern": [("Galle", 6.05, 80.22), ("Matara", 5.95, 80.55), ("Hambantota", 6.12, 81.12)],
    "Northern": [("Jaffna", 9.66, 80.01), ("Kilinochchi", 9.40, 80.40), ("Mannar", 8.98, 79.91),
                 ("Vavuniya", 8.75, 80.50), ("Mullaitivu", 9.27, 80.81)],
    "Eastern": [("Batticaloa", 7.73, 81.70), ("Ampara", 7.30, 81.67), ("Trincomalee", 8.57, 81.23)],
    "North Western": [("Kurunegala", 7.49, 80.37), ("Puttalam", 8.03, 79.83)],
    "North Central": [("Anuradhapura", 8.31, 80.40), ("Polonnaruwa", 7.94, 81.00)],
    "Uva": [("Badulla", 6.99, 81.06), ("Monaragala", 6.87, 81.35)],
    "Sabaragamuwa": [("Ratnapura", 6.68, 80.40), ("Kegalle", 7.25, 80.35)],
}

TYPES = {  # type -> (min_kw, max_kw)
    "rooftop": (5, 100),
    "ground": (500, 5000),
    "floating": (1000, 3000),
}


def solar_curve(hour: int) -> float:
    """0 at night, bell-shaped between 06:00 and 18:00 local time."""
    if 6 <= hour < 18:
        return math.sin(math.pi * (hour - 6 + 0.5) / 12)
    return 0.0


def main() -> None:
    rng = random.Random(SEED)
    db = SessionLocal()
    try:
        db.execute(text(
            "TRUNCATE readings, installations, users, districts, provinces RESTART IDENTITY CASCADE"
        ))

        # --- geography ---
        provinces: dict[str, Province] = {}
        districts: dict[str, District] = {}
        coords: dict[str, tuple[float, float]] = {}
        for pname, dlist in GEOGRAPHY.items():
            p = Province(name=pname)
            db.add(p)
            db.flush()
            provinces[pname] = p
            for dname, lat, lng in dlist:
                d = District(name=dname, province_id=p.id)
                db.add(d)
                db.flush()
                districts[dname] = d
                coords[dname] = (lat, lng)

        # --- installations ---
        installs: list[Installation] = []
        for dname, d in districts.items():
            lat0, lng0 = coords[dname]
            for n in range(1, rng.randint(2, 3) + 1):
                itype = rng.choice(list(TYPES))
                lo, hi = TYPES[itype]
                inst = Installation(
                    name=f"{dname} {itype.title()} Solar {n}",
                    capacity_kw=round(rng.uniform(lo, hi), 2),
                    installation_type=itype,
                    status="inactive" if rng.random() < 0.05 else "active",
                    latitude=round(lat0 + rng.uniform(-0.05, 0.05), 6),
                    longitude=round(lng0 + rng.uniform(-0.05, 0.05), 6),
                    commissioned_on=date(2019, 1, 1) + timedelta(days=rng.randint(0, 2400)),
                    district_id=d.id,
                )
                db.add(inst)
                installs.append(inst)
        db.flush()

        # --- users (dev passwords only) ---
        db.add_all([
            User(username="admin", hashed_password=pwd.hash("admin123"), role="admin"),
            User(username="western_officer", hashed_password=pwd.hash("western123"),
                 role="province", province_id=provinces["Western"].id),
            User(username="colombo_officer", hashed_password=pwd.hash("colombo123"),
                 role="district", district_id=districts["Colombo"].id),
        ])
        db.flush()

        # --- readings: hourly, inactive installations produce none ---
        total = 0
        batch: list[dict] = []
        for inst in installs:
            if inst.status != "active":
                continue
            cap = float(inst.capacity_kw)
            efficiency = rng.uniform(0.75, 0.9)
            for day in range(DAYS):
                cloud = rng.uniform(0.35, 1.0)  # daily weather factor
                for hour in range(24):
                    ts = START + timedelta(days=day, hours=hour)
                    power = cap * solar_curve(hour) * efficiency * cloud * rng.uniform(0.95, 1.0)
                    batch.append({
                        "installation_id": inst.id,
                        "recorded_at": ts,
                        "power_kw": round(power, 3),
                        "energy_kwh": round(power, 3),  # 1-hour interval -> kWh == average kW
                    })
                    if len(batch) >= 5000:
                        db.execute(insert(Reading), batch)
                        total += len(batch)
                        batch = []
        if batch:
            db.execute(insert(Reading), batch)
            total += len(batch)

        db.commit()
        print(f"Provinces: {len(provinces)}, districts: {len(districts)}, "
              f"installations: {len(installs)}, readings: {total}, users: 3")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()