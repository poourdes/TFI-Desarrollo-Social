from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.public_areas import router as public_areas_router
from app.api.routes.public_reports import router as public_reports_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(public_areas_router, prefix=settings.api_v1_prefix)
app.include_router(public_reports_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
