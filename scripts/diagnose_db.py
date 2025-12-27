import asyncio
from sqlalchemy import select, func
from bot.database.database import sessionmaker
from bot.database.models import UserModel, GameRecordModel

async def diagnose():
    async with sessionmaker() as session:
        users = await session.execute(select(UserModel))
        for user in users.scalars().all():
            print(f"User {user.id} ({user.first_name}): total_games={user.total_games}")
            
            # Show last 10 records with timestamps
            records = await session.execute(
                select(GameRecordModel)
                .where(GameRecordModel.user_id == user.id)
                .order_by(GameRecordModel.created_at.desc())
                .limit(10)
            )
            for r in records.scalars().all():
                print(f"  [{r.created_at}] Mode: {r.game_mode}, Win: {r.is_win}, Score: {r.score}")

if __name__ == "__main__":
    asyncio.run(diagnose())
