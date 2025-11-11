from fastapi import APIRouter
from . import routes_health, routes_auth, routes_reports, routes_ml, routes_departments

api_router = APIRouter()
api_router.include_router(routes_health.router, tags=["health"])
api_router.include_router(routes_auth.router)
api_router.include_router(routes_reports.router)
api_router.include_router(routes_ml.router)
api_router.include_router(routes_departments.router)