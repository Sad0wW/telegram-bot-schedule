from aiogram import Router

from .edit_about import router as edit_about_router
from .users import router as users_router
from .grades import router as grades_router

router = Router()

router.include_routers(
    edit_about_router,
    users_router,
    grades_router
)