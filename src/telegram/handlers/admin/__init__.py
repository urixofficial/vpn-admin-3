from aiogram import Router

from .user_control import router as user_control_router

router = Router(name="admin_router")
router.include_router(user_control_router)

__all__ = {"router"}