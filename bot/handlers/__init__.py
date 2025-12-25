from aiogram import Router

from . import start, web_app, profile, leaderboard, admin


def get_handlers_router() -> Router:
    router = Router()
    router.include_router(start.router)
    router.include_router(web_app.router)
    router.include_router(profile.router)
    router.include_router(leaderboard.router)
    router.include_router(admin.router)

    return router
