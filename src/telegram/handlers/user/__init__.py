from aiogram import Router
from .registration import router as registration_router
from .payment import router as user_payment_router
from .common import router as common_user_router
from .instructions import router as instructions_router

router = Router(name="user_router")
router.include_router(common_user_router)
router.include_router(registration_router)
router.include_router(user_payment_router)
router.include_router(instructions_router)

__all__ = {"router"}
