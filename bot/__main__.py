from __future__ import annotations
import asyncio

import sentry_sdk
import uvloop
from loguru import logger
from sentry_sdk.integrations.loguru import LoggingLevels, LoguruIntegration

from bot.core.config import settings
from bot.core.loader import app, bot, dp
from bot.handlers import get_handlers_router
from bot.keyboards.default_commands import remove_default_commands, set_default_commands
from bot.middlewares import register_middlewares
from bot.middlewares.prometheus import prometheus_middleware_factory


async def on_startup() -> None:
    logger.info("bot starting...")

    register_middlewares(dp)

    dp.include_router(get_handlers_router())

    if settings.USE_WEBHOOK:
        app.middlewares.append(prometheus_middleware_factory())


    await set_default_commands(bot)

    bot_info = await bot.get_me()

    logger.info(f"Name     - {bot_info.full_name}")
    logger.info(f"Username - @{bot_info.username}")
    logger.info(f"ID       - {bot_info.id}")

    states: dict[bool | None, str] = {
        True: "Enabled",
        False: "Disabled",
        None: "Unknown (This's not a bot)",
    }

    logger.info(f"Groups Mode  - {states[bot_info.can_join_groups]}")
    logger.info(f"Privacy Mode - {states[not bot_info.can_read_all_group_messages]}")
    logger.info(f"Inline Mode  - {states[bot_info.supports_inline_queries]}")

    logger.info("bot started")


async def on_shutdown() -> None:
    logger.info("bot stopping...")

    await remove_default_commands(bot)

    await dp.storage.close()
    await dp.fsm.storage.close()

    await bot.delete_webhook()
    await bot.session.close()

    logger.info("bot stopped")


async def main() -> None:
    if settings.SENTRY_DSN:
        sentry_loguru = LoguruIntegration(
            level=LoggingLevels.INFO.value,
            event_level=LoggingLevels.INFO.value,
        )
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            integrations=[sentry_loguru],
        )

    logger.add(
        "logs/telegram_bot.log",
        level="DEBUG",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="100 KB",
        compression="zip",
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Use Uvicorn to run the FastAPI app
    import uvicorn
    from bot.api.main import app as fastapi_app

    config = uvicorn.Config(
        app=fastapi_app,
        host=settings.WEBHOOK_HOST,
        port=settings.WEBHOOK_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)

    if settings.USE_WEBHOOK:
        # In webhook mode, Uvicorn handles the server
        # We need to ensure webhook is set during startup
        @fastapi_app.on_event("startup")
        async def on_fastapi_startup():
            try:
                await bot.set_webhook(
                    settings.webhook_url,
                    allowed_updates=dp.resolve_used_update_types(),
                    secret_token=settings.WEBHOOK_SECRET,
                    request_timeout=30,
                )
                logger.info("Webhook set successfully")
            except Exception as e:
                logger.exception(f"Failed to set webhook: {e}")

        
        await server.serve()
    else:
        # In polling mode, we run polling AND the server (for Web App)
        # We run them concurrently
        await bot.delete_webhook(drop_pending_updates=True)
        
        # Run polling + server
        # We need to run server in a way that doesn't block polling
        # Since uvicorn.Server.serve() is a blocking loop, we task it.
        params = {"allowed_updates": dp.resolve_used_update_types()}
        
        # Start the API server in bg
        asyncio.create_task(server.serve())
        
        await dp.start_polling(bot, **params)


if __name__ == "__main__":
    try:
        if asyncio.get_event_loop().is_running():
            asyncio.create_task(main())
        else:
            uvloop.run(main()) # uvloop for linux
    except RuntimeError:
        # Fallback for systems where uvloop might conflict or other loop issues
        asyncio.run(main())
