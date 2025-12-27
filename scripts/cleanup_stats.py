import asyncio
from sqlalchemy import select, func, update
from bot.database.database import sessionmaker
from bot.database.models import UserModel, GameRecordModel

async def cleanup():
    async with sessionmaker() as session:
        users = await session.execute(select(UserModel))
        users = users.scalars().all()
        
        for user in users:
            # Count actual records
            records_count = await session.scalar(
                select(func.count()).select_from(GameRecordModel).where(GameRecordModel.user_id == user.id)
            )
            print(f"Syncing user {user.id}: {user.total_games} -> {records_count}")
            user.total_games = records_count
        
        await session.commit()
        print("Done!")

if __name__ == "__main__":
    asyncio.run(cleanup())
