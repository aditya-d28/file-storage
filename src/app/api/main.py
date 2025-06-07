from fastapi import APIRouter

from app.api.routes import delete, list, upload

api_router = APIRouter()

api_router.include_router(upload.router, tags=["rest-service"])
api_router.include_router(delete.router, tags=["rest-service"])
api_router.include_router(list.router, tags=["rest-service"])
