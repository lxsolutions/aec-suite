from fastapi import APIRouter
from . import estimates, projects, health
router = APIRouter()
router.include_router(estimates.router)
router.include_router(projects.router)
router.include_router(health.router)
