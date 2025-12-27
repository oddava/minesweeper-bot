from aiogram import Router, types
from aiogram.filters import Command
from bot.core.config import VERSION
from aiogram.utils.i18n import gettext as _

router = Router(name="about")

@router.message(Command("version"))
async def version_handler(message: types.Message):
    """Show current bot version."""
    await message.answer(f"🤖 <b>Minesweeper Bot</b>\nVersion: <code>{VERSION}</code>", parse_mode="HTML")

@router.message(Command("changelog"))
async def changelog_handler(message: types.Message):
    """Show the latest changes."""
    text = _("""
<b>🆕 What's New in {version}</b>

✅ <b>Fixes</b>
- Accurate statistics calculation.
- Improved local development environment.
- Hardened game counting & de-duplication.

🚀 <b>Features</b>
- Professional versioning system.
- This changelog command!
- Version display in the WebApp.

<i>Type /support if you find any bugs!</i>
""").format(version=VERSION)
    await message.answer(text.strip(), parse_mode="HTML")
