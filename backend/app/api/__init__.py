"""API routers package."""
from app.api import auth, candidates, applications, joining_notices, employees, dashboard

__all__ = [
    "auth",
    "candidates",
    "applications",
    "joining_notices",
    "employees",
    "dashboard",
]
