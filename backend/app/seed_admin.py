import argparse
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.data.admin import seed_admin_user
from app.data.areas import seed_areas

DEFAULT_AREAS = "adultos-mayores"


def main() -> None:
    parser = argparse.ArgumentParser(description="Crear o actualizar el usuario admin")
    parser.add_argument("--email", default=os.getenv("ADMIN_EMAIL"))
    parser.add_argument("--password", default=os.getenv("ADMIN_PASSWORD"))
    parser.add_argument(
        "--full-name", default=os.getenv("ADMIN_FULL_NAME", "Administrador")
    )
    parser.add_argument("--areas", default=os.getenv("ADMIN_AREAS", DEFAULT_AREAS))
    args = parser.parse_args()

    if not args.email or not args.password:
        parser.error("Se requieren --email/ADMIN_EMAIL y --password/ADMIN_PASSWORD")

    area_slugs = [slug.strip() for slug in args.areas.split(",") if slug.strip()]
    engine = create_engine(settings.database_url)
    with Session(engine) as db:
        seed_areas(db)
        user = seed_admin_user(
            db,
            email=args.email,
            password=args.password,
            full_name=args.full_name,
            area_slugs=area_slugs,
        )
    print(f"Admin listo: {user.email} ({', '.join(area_slugs)})")


if __name__ == "__main__":
    main()
