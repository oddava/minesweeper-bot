import logging
from aiogram.filters import BaseFilter
from aiogram.types import Message
from bot.core.config import settings
from bot.database.database import sessionmaker
from bot.database.models import UserModel


class IsSuperadmin(BaseFilter):
    """Filter for superadmin-only commands"""
    
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
        
        is_super = message.from_user.id == settings.SUPERADMIN_ID
        if not is_super:
            logging.warning(f"IsSuperadmin check failed: {message.from_user.id} != {settings.SUPERADMIN_ID}")
        return is_super


class IsAdmin(BaseFilter):
    """Filter for admin commands (includes superadmin)"""
    
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
            
        user_id = message.from_user.id
        
        # Superadmin is always admin
        if user_id == settings.SUPERADMIN_ID:
            return True
        
        # Check database for admin status
        async with sessionmaker() as session:
            user = await session.get(UserModel, user_id)
            if user and user.is_admin:
                return True
        
        logging.warning(f"IsAdmin check failed for user {user_id}")
        return False

