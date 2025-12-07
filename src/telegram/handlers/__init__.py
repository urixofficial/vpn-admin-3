from aiogram import Router

from .common import router as common_router
from .user import router as user_router
from .admin import router as admin_router

router = Router(name="main_router")
router.include_router(common_router)
router.include_router(admin_router)
router.include_router(user_router)

__all__ = {"router"}
