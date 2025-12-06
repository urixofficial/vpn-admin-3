from aiogram import Router
from .common import router as common_awg_router
from .read import router as read_awg_router
from .delete import router as delete_awg_router

router = Router()
router.include_router(common_awg_router)
router.include_router(read_awg_router)
router.include_router(delete_awg_router)
