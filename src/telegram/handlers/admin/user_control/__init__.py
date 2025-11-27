from aiogram import Router

from .common import router as user_control_panel_router
from .create import router as create_user_router
from .read import router as read_user_router
from .update import router as update_user_router
from .delete import router as delete_user_router

router = Router(name="user_control_router")
router.include_router(user_control_panel_router)
router.include_router(create_user_router)
router.include_router(read_user_router)
router.include_router(update_user_router)
router.include_router(delete_user_router)

__all__ = {router}