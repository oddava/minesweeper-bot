from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select, func
from bot.database.database import sessionmaker
from bot.database.models import UserModel, GameRecordModel
from bot.filters.admin import IsSuperadmin, IsAdmin
from bot.core.config import settings

router = Router(name="admin")

# ============ SUPERADMIN COMMANDS ============

@router.message(Command("admin"), IsSuperadmin())
async def admin_help(message: types.Message):
    """Admin panel help"""
    args = message.text.split()
    
    # If it's just /admin, show help
    if len(args) == 1:
        text = """
<b>👑 Admin Panel</b>

<b>Superadmin Commands:</b>
/admin add <code>&lt;user_id&gt;</code> — Add admin
/admin remove <code>&lt;user_id&gt;</code> — Remove admin
/admin list — List all admins
/broadcast <code>&lt;message&gt;</code> — Broadcast to all users
/config — Show bot configuration

<b>Admin Commands:</b>
/stats — Bot statistics
/userstats <code>&lt;user_id&gt;</code> — View user stats
/ban <code>&lt;user_id&gt;</code> — Ban user
/unban <code>&lt;user_id&gt;</code> — Unban user
/suspicious — List suspicious users
/resetstats <code>&lt;user_id&gt;</code> — Reset user stats
"""
        return await message.answer(text.strip(), parse_mode="HTML")

    # Handle subcommands
    subcommand = args[1].lower()
    
    if subcommand == "add":
        return await admin_add(message)
    elif subcommand == "remove":
        return await admin_remove(message)
    elif subcommand == "list":
        return await admin_list(message)
    else:
        await message.answer(f"❓ Unknown subcommand: {subcommand}")


# Helper functions called from admin_help
async def admin_add(message: types.Message):
    """Add a new admin"""
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: /admin add <user_id>")
        return
    
    try:
        user_id = int(args[2])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("❌ User not found. They must use the bot first.")
            return
        
        user.is_admin = True
        await session.commit()
        await message.answer(f"✅ User <code>{user_id}</code> ({user.first_name}) is now an admin!", parse_mode="HTML")


async def admin_remove(message: types.Message):
    """Remove an admin"""
    args = message.text.split()
    if len(args) < 3:
        await message.answer("Usage: /admin remove <user_id>")
        return
    
    try:
        user_id = int(args[2])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("❌ User not found")
            return
        
        user.is_admin = False
        await session.commit()
        await message.answer(f"✅ User <code>{user_id}</code> is no longer an admin.", parse_mode="HTML")


async def admin_list(message: types.Message):
    """List all admins"""
    async with sessionmaker() as session:
        query = select(UserModel).where(UserModel.is_admin == True)
        result = await session.execute(query)
        admins = result.scalars().all()
        
        text = f"<b>👑 Superadmin:</b> <code>{settings.SUPERADMIN_ID}</code>\n\n"
        
        if admins:
            text += "<b>👮 Admins:</b>\n"
            for admin in admins:
                text += f"• {admin.first_name} (<code>{admin.id}</code>)\n"
        else:
            text += "<i>No additional admins</i>"
        
        await message.answer(text, parse_mode="HTML")


@router.message(Command("config"), IsSuperadmin())
async def config_handler(message: types.Message):
    """Show current configuration for debugging"""
    text = f"""
<b>⚙️ Bot Configuration</b>

<b>Superadmin ID:</b> <code>{settings.SUPERADMIN_ID}</code>
<b>Webhook Host:</b> <code>{settings.WEBHOOK_HOST}</code>
<b>Webhook Port:</b> <code>{settings.WEBHOOK_PORT}</code>
<b>Webhook Base URL:</b> <code>{settings.WEBHOOK_BASE_URL}</code>
<b>Webhook Path:</b> <code>{settings.WEBHOOK_PATH}</code>
<b>Use Webhook:</b> <code>{settings.USE_WEBHOOK}</code>
<b>Database User:</b> <code>{settings.DB_USER}</code>
<b>Database Name:</b> <code>{settings.DB_NAME}</code>
"""
    await message.answer(text.strip(), parse_mode="HTML")


@router.message(Command("broadcast"), IsSuperadmin())
async def broadcast(message: types.Message):
    """Broadcast message to all users"""
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Usage: /broadcast <message>")
        return
    
    async with sessionmaker() as session:
        query = select(UserModel.id).where(UserModel.is_block == False)
        result = await session.execute(query)
        user_ids = result.scalars().all()
    
    sent = 0
    failed = 0
    from bot.core.loader import bot
    
    for user_id in user_ids:
        try:
            await bot.send_message(user_id, text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
    
    await message.answer(f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")


# ============ ADMIN COMMANDS ============

@router.message(Command("stats"), IsAdmin())
async def stats_handler(message: types.Message):
    """Bot statistics"""
    async with sessionmaker() as session:
        # Total users
        users_count = await session.scalar(select(func.count()).select_from(UserModel))
        
        # Total games
        games_count = await session.scalar(select(func.count()).select_from(GameRecordModel))
        
        # Wins
        wins_count = await session.scalar(
            select(func.count()).select_from(GameRecordModel).where(GameRecordModel.is_win == True)
        )
        
        # Suspicious users
        suspicious_count = await session.scalar(
            select(func.count()).select_from(UserModel).where(UserModel.is_suspicious == True)
        )
        
        # Blocked users
        blocked_count = await session.scalar(
            select(func.count()).select_from(UserModel).where(UserModel.is_block == True)
        )
    
    text = f"""
<b>📊 Bot Statistics</b>

👥 Total Users: <b>{users_count}</b>
🎮 Total Games: <b>{games_count}</b>
🏆 Total Wins: <b>{wins_count}</b>
⚠️ Suspicious Users: <b>{suspicious_count}</b>
🚫 Blocked Users: <b>{blocked_count}</b>
"""
    await message.answer(text.strip(), parse_mode="HTML")


@router.message(Command("userstats"), IsAdmin())
async def userstats_handler(message: types.Message):
    """View specific user's stats"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /userstats <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("❌ User not found")
            return
        
        # Get mode stats
        modes = ["beginner", "intermediate", "expert"]
        mode_stats = []
        
        for mode in modes:
            wins = await session.scalar(
                select(func.count()).select_from(GameRecordModel).where(
                    GameRecordModel.user_id == user_id,
                    GameRecordModel.game_mode == mode,
                    GameRecordModel.is_win == True
                )
            ) or 0
            
            best_time = await session.scalar(
                select(func.min(GameRecordModel.score)).where(
                    GameRecordModel.user_id == user_id,
                    GameRecordModel.game_mode == mode,
                    GameRecordModel.is_win == True
                )
            )
            
            time_str = f"{best_time}s" if best_time else "—"
            mode_stats.append(f"  {mode.title()}: {wins} wins, best {time_str}")
    
    flags = []
    if user.is_superadmin: flags.append("👑 Superadmin")
    if user.is_admin: flags.append("👮 Admin")
    if user.is_suspicious: flags.append("⚠️ Suspicious")
    if user.is_block: flags.append("🚫 Blocked")
    
    text = f"""
<b>👤 User Stats</b>

<b>ID:</b> <code>{user.id}</code>
<b>Name:</b> {user.first_name} {user.last_name or ''}
<b>Username:</b> @{user.username or '—'}
<b>Flags:</b> {', '.join(flags) if flags else 'None'}

<b>Game Stats:</b>
🎮 Total Games: {user.total_games}
🔥 Current Streak: {user.current_streak}
🏆 Best Streak: {user.best_streak}

<b>Mode Stats:</b>
{chr(10).join(mode_stats)}
"""
    await message.answer(text.strip(), parse_mode="HTML")


@router.message(Command("ban"), IsAdmin())
async def ban_handler(message: types.Message):
    """Ban a user"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    if user_id == settings.SUPERADMIN_ID:
        await message.answer("❌ Cannot ban superadmin")
        return
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("❌ User not found")
            return
        
        user.is_block = True
        await session.commit()
        await message.answer(f"🚫 User <code>{user_id}</code> has been banned.", parse_mode="HTML")


@router.message(Command("unban"), IsAdmin())
async def unban_handler(message: types.Message):
    """Unban a user"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("❌ User not found")
            return
        
        user.is_block = False
        await session.commit()
        await message.answer(f"✅ User <code>{user_id}</code> has been unbanned.", parse_mode="HTML")


@router.message(Command("suspicious"), IsAdmin())
async def suspicious_handler(message: types.Message):
    """List suspicious users"""
    async with sessionmaker() as session:
        query = select(UserModel).where(UserModel.is_suspicious == True).limit(20)
        result = await session.execute(query)
        users = result.scalars().all()
        
        if not users:
            await message.answer("✅ No suspicious users!")
            return
        
        text = "<b>⚠️ Suspicious Users</b>\n\n"
        for user in users:
            text += f"• {user.first_name} (<code>{user.id}</code>)\n"
        
        await message.answer(text, parse_mode="HTML")


@router.message(Command("resetstats"), IsAdmin())
async def resetstats_handler(message: types.Message):
    """Reset user's game stats"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /resetstats <user_id>")
        return
    
    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ Invalid user ID")
        return
    
    async with sessionmaker() as session:
        user = await session.get(UserModel, user_id)
        if not user:
            await message.answer("❌ User not found")
            return
        
        user.total_games = 0
        user.current_streak = 0
        user.best_streak = 0
        user.is_suspicious = False
        await session.commit()
        
        await message.answer(f"✅ Stats reset for user <code>{user_id}</code>", parse_mode="HTML")
