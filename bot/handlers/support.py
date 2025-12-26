from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from bot.core.config import settings

router = Router(name="support")

@router.message(Command("support"))
async def support_handler(message: types.Message) -> None:
    """Send support URL."""
    if settings.SUPPORT_URL:
        await message.answer(_("If you have any questions or issues, please contact our support: {url}").format(url=settings.SUPPORT_URL))
    else:
        await message.answer(_("Support is currently unavailable."))
