from aiogram import Router

from .common import router as common_router
from .user_control import router as user_control_router
from .transaction_control import router as transaction_control_router

router = Router(name="admin_router")
router.include_router(common_router)
router.include_router(user_control_router)
router.include_router(transaction_control_router)

__all__ = {"router"}
