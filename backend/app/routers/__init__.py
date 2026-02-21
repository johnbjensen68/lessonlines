from .events import router as events_router
from .standards import router as standards_router
from .timelines import router as timelines_router
from .auth import router as auth_router
from .users import router as users_router
from .export import router as export_router
from .candidates import router as candidates_router

__all__ = [
    "events_router",
    "standards_router",
    "timelines_router",
    "auth_router",
    "users_router",
    "export_router",
    "candidates_router",
]
