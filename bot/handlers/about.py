from aiogram import Router, types
from aiogram.filters import Command
from bot.core.config import VERSION
from aiogram.utils.i18n import gettext as _

router = Router(name="about")

@router.message(Command("changelog"))
async def changelog_handler(message: types.Message):
    """Show the latest changes."""
    text = _("""
<b>🆕 What's New in {version}</b>

🎨 <b>Themes</b>
- 5 themes: Classic, Neon, Ocean, Retro, New Year Eve 🎆
- Settings persist across sessions

⚡ <b>Performance</b>
- WebApp optimized and 4x lighter
- Faster loading, smoother gameplay

✨ <b>UI Improvements</b>
- Renamed to "oddava's minesweeper"
- Game stats on win/lose (time, clicks, flags)
- Scrollable board for Expert mode

<i>Type /support if you find any bugs!</i>
""").format(version=VERSION)
    await message.answer(text.strip(), parse_mode="HTML")
