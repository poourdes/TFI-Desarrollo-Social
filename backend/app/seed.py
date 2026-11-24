"""Database seed entrypoint.

Runs against the configured DATABASE_URL (SQLite or PostgreSQL) and upserts
the area definitions used by the public reporting flow.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.areas import seed_areas


def main() -> None:
    engine = create_engine(settings.database_url)
    with Session(engine) as session:
        seed_areas(session)
    print(f"Seed completed. Database: {settings.database_url}")
    print("Five areas upserted.")


if __name__ == "__main__":
    main()
