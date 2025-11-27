from aiogram import Router

from .common import router as transaction_control_panel_router
from .create import router as transaction_create_router
from .read import router as transaction_read_router
from .delete import router as transaction_delete_router

router = Router(name="transaction_control_router")
router.include_router(transaction_control_panel_router)
router.include_router(transaction_create_router)
router.include_router(transaction_read_router)
router.include_router(transaction_delete_router)

__all__ = {"router"}