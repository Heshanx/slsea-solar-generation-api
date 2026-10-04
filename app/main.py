from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db


def create_app() -> FastAPI:
    app = FastAPI(
        title="SLSEA Solar Generation API",
        version="0.1.0",
        description="Real-time and historical solar generation data for Sri Lanka.",
    )

    @app.get("/health", tags=["system"])
    def health(db: Session = Depends(get_db)):
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}

    return app


app = create_app()