from aiogram import Router

from .common import router as common_router
from .user_control import router as user_control_router
from .transaction_control import router as transaction_control_router
from .awg_control import router as awg_control_router
from .broadcast import router as messages_router

router = Router(name="admin_router")
router.include_router(common_router)
router.include_router(user_control_router)
router.include_router(transaction_control_router)
router.include_router(awg_control_router)
router.include_router(messages_router)


__all__ = {"router"}
