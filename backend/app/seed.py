"""Database seed entrypoint.

Runs against the configured DATABASE_URL (SQLite or PostgreSQL).
Domain seed data will be added in later phases.
"""

from sqlalchemy import create_engine, text

from app.core.config import settings


def main() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print(f"Seed completed. Database: {settings.database_url}")
    print("No domain seed data defined yet.")


if __name__ == "__main__":
    main()
