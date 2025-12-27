from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy import select, func
from bot.database.database import sessionmaker
from bot.database.models import UserModel, GameRecordModel

router = Router(name="profile")

@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    """Show player stats"""
    user_id = message.from_user.id
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("You haven't played any games yet! Send /play to start.")
            return
        
        # Get stats per mode
        modes = ["beginner", "intermediate", "expert"]
        stats_text = []
        
        for mode in modes:
            # Count wins
            wins_query = select(func.count()).select_from(GameRecordModel).where(
                GameRecordModel.user_id == user_id,
                GameRecordModel.game_mode == mode,
                GameRecordModel.is_win == True
            )
            wins_result = await session.execute(wins_query)
            wins = wins_result.scalar() or 0
            
            # Best time
            best_time_query = select(func.min(GameRecordModel.score)).where(
                GameRecordModel.user_id == user_id,
                GameRecordModel.game_mode == mode,
                GameRecordModel.is_win == True
            )
            best_time_result = await session.execute(best_time_query)
            best_time = best_time_result.scalar()
            
            mode_emoji = {"beginner": "🟢", "intermediate": "🟡", "expert": "🔴"}[mode]
            time_str = f"{best_time}s" if best_time else "—"
            stats_text.append(f"{mode_emoji} <b>{mode.title()}</b>: {wins} wins | Best: {time_str}")
        
        text = f"""
<b>📊 Your Stats</b>

🎮 Total Games: <b>{user.total_games}</b>
🔥 Current Streak: <b>{user.current_streak}</b>
🏆 Best Streak: <b>{user.best_streak}</b>

<b>Mode Stats:</b>
{chr(10).join(stats_text)}
"""
        await message.answer(text.strip(), parse_mode="HTML")
