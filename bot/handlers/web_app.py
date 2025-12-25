from aiogram import Router, types
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from bot.core.config import settings

router = Router(name="web_app")

@router.message(Command("play"))
async def play_handler(message: types.Message):
    """
    Handler for /play command.
    Sends a button to open the Minesweeper Web App.
    """
    # Construct the Web App URL
    # If running with ngrok, we need the public HTTPS url
    # We use WEBHOOK_BASE_URL from settings which should be the ngrok url
    web_app_url = f"{settings.WEBHOOK_BASE_URL}/game/index.html"
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎮 Play Minesweeper",
            web_app=WebAppInfo(url=web_app_url)
        )]
    ])
    
    await message.answer(
        "💣 <b>Minesweeper Ready!</b>\n\nClick the button below to launch the game.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
