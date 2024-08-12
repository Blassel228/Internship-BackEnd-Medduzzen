from typing import Dict
from fastapi import APIRouter

health_check_router = APIRouter()


@health_check_router.get("/", response_model=Dict[str, str])
def read_root() -> Dict[str, str]:
    """
    Root endpoint to check if the API is working.
    """
    return {"status_code": "200", "detail": "ok", "github-actions": "working1"}


@health_check_router.get("/health_check", response_model=Dict[str, str])
def health_check() -> Dict[str, str]:
    """
    Health check endpoint to verify the health of the application.
    """
    return {"status_code": "200", "detail": "ok", "result": "healthy", "github-actions": "working"}
