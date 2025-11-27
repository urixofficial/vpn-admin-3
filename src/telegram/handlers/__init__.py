from aiogram import Router

from .admin import router as admin_router

router = Router(name="main_router")
router.include_router(admin_router)

__all__ = {"router"}