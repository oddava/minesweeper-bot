from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func, desc
from bot.database.database import sessionmaker
from bot.database.models import UserModel, GameRecordModel

router = Router(name="leaderboard")

def get_refresh_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_leaderboard")]
    ])

async def get_leaderboard_text():
    async with sessionmaker() as session:
        modes = ["beginner", "intermediate", "expert"]
        mode_emoji = {"beginner": "🟢", "intermediate": "🟡", "expert": "🔴"}
        
        text_parts = ["<b>🏆 Leaderboard</b>\n"]
        
        for mode in modes:
            query = (
                select(
                    UserModel.first_name,
                    func.min(GameRecordModel.score).label("best_time")
                )
                .join(UserModel, GameRecordModel.user_id == UserModel.id)
                .where(GameRecordModel.game_mode == mode, GameRecordModel.is_win == True)
                .group_by(UserModel.id, UserModel.first_name)
                .order_by("best_time")
                .limit(5)
            )
            result = await session.execute(query)
            rows = result.all()
            
            if rows:
                text_parts.append(f"\n{mode_emoji[mode]} <b>{mode.title()}</b>")
                for i, row in enumerate(rows):
                    medal = ["🥇", "🥈", "🥉", "4.", "5."][i]
                    text_parts.append(f"{medal} {row.first_name} — {row.best_time}s")
        
        if len(text_parts) == 1:
            return None
        
        return "\n".join(text_parts)

@router.message(Command("leaderboard"))
async def leaderboard_handler(message: types.Message):
    """Show top players for each mode"""
    text = await get_leaderboard_text()
    if not text:
        await message.answer("No games played yet! Be the first to set a record.")
        return
    
    await message.answer(text, parse_mode="HTML", reply_markup=get_refresh_keyboard())

@router.callback_query(F.data == "refresh_leaderboard")
async def refresh_leaderboard_callback(callback: types.CallbackQuery):
    """Refresh the leaderboard"""
    text = await get_leaderboard_text()
    if not text:
        await callback.answer("No data yet!")
        return
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=get_refresh_keyboard())
    await callback.answer("Refreshed! ✅")

