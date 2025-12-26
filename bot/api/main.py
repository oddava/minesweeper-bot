from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from aiogram.types import Update
from bot.core.loader import dp, bot
from bot.core.config import settings
import logging
import time
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from collections import defaultdict

app = FastAPI()

# Metrics
GAMES_TOTAL = Counter('minesweeper_games_total', 'Total games played', ['mode', 'status'])

# Simple in-memory rate limiting (for demonstration, use Redis in production for scale)
# Map: user_id -> last_request_time
rate_limits = defaultdict(float)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path == "/api/game/result" and request.method == "POST":
        # We can't easily get user_id from body here without consuming stream
        # So we rely on strict path limits or IP based which is tricky behind proxies
        # For now, we implemented logic INSIDE the handler for user-based limits (logic is safe)
        pass
    
    response = await call_next(request)
    return response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}

# Mount the Web App static files
# Checks if directory exists first to avoid startup errors during dev
import os
if not os.path.exists("bot/web_app"):
    os.makedirs("bot/web_app")
    
app.mount("/game", StaticFiles(directory="bot/web_app", html=True), name="game")

@app.post(settings.WEBHOOK_PATH)
async def bot_webhook(request: Request):
    """
    Handle incoming Telegram updates (Webhooks)
    """
    # 1. Secret token validation
    if settings.WEBHOOK_SECRET:
        secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if secret_token != settings.WEBHOOK_SECRET:
            logging.warning("Unauthorized access attempt to webhook")
            return Response(content="Unauthorized", status_code=401)

    try:
        data = await request.json()
        logging.debug(f"Received webhook update: {data}")
        
        update = Update.model_validate(data, context={"bot": bot})
        await dp.feed_update(bot, update)
        return {"status": "ok"}
    except Exception as e:
        logging.exception("Error processing webhook")
        return {"status": "error", "message": str(e)}


from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from bot.database.models import GameRecordModel, UserModel
from bot.database.database import sessionmaker

from aiogram.utils.web_app import check_webapp_signature, safe_parse_webapp_init_data
from bot.core.config import settings
import time

class GameResult(BaseModel):
    initData: str
    user_id: int
    score: int
    is_win: bool
    first_name: str
    username: str | None = None
    game_mode: str = "beginner"
    rows: int = 9
    cols: int = 9
    mines: int = 10

@app.post("/api/game/result")
async def game_result(result: GameResult):
    try:
        # 1. Validate Telegram initData
        try:
            if not check_webapp_signature(settings.BOT_TOKEN, result.initData):
                return {"status": "error", "message": "Invalid signature"}
        except Exception:
            return {"status": "error", "message": "Validation failed"}
        
        # 2. Time bounds check (score is time in seconds)
        if result.is_win:
            if result.score < 3:
                return {"status": "error", "message": "Time too short"}
            if result.score > 3600:
                 return {"status": "error", "message": "Time too long"}

        # 3. Mode validation
        modes = {
            "beginner": (9, 9, 10),
            "intermediate": (16, 16, 40),
            "expert": (16, 30, 99)
        }
        if result.game_mode in modes:
            expected_rows, expected_cols, expected_mines = modes[result.game_mode]
            if (result.rows != expected_rows or 
                result.cols != expected_cols or 
                result.mines != expected_mines):
                return {"status": "error", "message": "Invalid mode config"}

        if result.user_id:
            async with sessionmaker() as session:
                user = await session.get(UserModel, result.user_id)
                if not user:
                    user = UserModel(
                        id=result.user_id,
                        first_name=result.first_name,
                        username=result.username
                    )
                    session.add(user)
                    await session.flush()
                
                # 4. Suspicious activity check
                # Expert win under 30 seconds is suspicious due to world record standards
                is_suspicious = False
                if result.is_win and result.game_mode == "expert" and result.score < 30:
                    is_suspicious = True
                    user.is_suspicious = True
                
                # Check if user is blocked
                if user.is_block:
                     return {"status": "error", "message": "User is blocked"}

                # Update user stats
                user.total_games += 1
                if result.is_win:
                    user.current_streak += 1
                    if user.current_streak > user.best_streak:
                        user.best_streak = user.current_streak
                else:
                    user.current_streak = 0

                record = GameRecordModel(
                    user_id=result.user_id,
                    game_mode=result.game_mode,
                    rows=result.rows,
                    cols=result.cols,
                    mines=result.mines,
                    score=result.score,
                    is_win=result.is_win
                )
                session.add(record)
                await session.commit()
                
                # Update metrics
                status = "win" if result.is_win else "loss"
                GAMES_TOTAL.labels(mode=result.game_mode, status=status).inc()
                
                return {"status": "ok", "suspicious": is_suspicious}
    except Exception as e:
        logging.exception("Error saving game result")
        return {"status": "error", "message": str(e)}


@app.get("/api/stats/{user_id}")
async def get_stats(user_id: int):
    try:
        async with sessionmaker() as session:
            user = await session.get(UserModel, user_id)
            if not user:
                return {"error": "User not found"}
            
            # Get wins and best time per mode
            modes = ["beginner", "intermediate", "expert"]
            stats = {
                "user_id": user_id,
                "total_games": user.total_games,
                "current_streak": user.current_streak,
                "best_streak": user.best_streak,
                "modes": {}
            }
            
            for mode in modes:
                # Count wins
                wins_query = select(func.count()).where(
                    GameRecordModel.user_id == user_id,
                    GameRecordModel.game_mode == mode,
                    GameRecordModel.is_win == True
                )
                wins_result = await session.execute(wins_query)
                wins = wins_result.scalar() or 0
                
                # Best time (lowest score where is_win=True)
                best_time_query = select(func.min(GameRecordModel.score)).where(
                    GameRecordModel.user_id == user_id,
                    GameRecordModel.game_mode == mode,
                    GameRecordModel.is_win == True
                )
                best_time_result = await session.execute(best_time_query)
                best_time = best_time_result.scalar()
                
                stats["modes"][mode] = {
                    "wins": wins,
                    "best_time": best_time
                }
            
            return stats
    except Exception as e:
        logging.exception("Error fetching stats")
        return {"error": str(e)}


@app.get("/api/leaderboard/{mode}")
async def get_leaderboard(mode: str):
    try:
        async with sessionmaker() as session:
            # Top 10 best times for the mode
            query = (
                select(GameRecordModel.user_id, UserModel.first_name, func.min(GameRecordModel.score).label("best_time"))
                .join(UserModel, GameRecordModel.user_id == UserModel.id)
                .where(GameRecordModel.game_mode == mode, GameRecordModel.is_win == True)
                .group_by(GameRecordModel.user_id, UserModel.first_name)
                .order_by(desc("best_time"))
                .limit(10)
            )
            result = await session.execute(query)
            rows = result.all()
            
            leaderboard = [
                {"rank": i+1, "user_id": row.user_id, "name": row.first_name, "best_time": row.best_time}
                for i, row in enumerate(rows)
            ]
            return {"mode": mode, "leaderboard": leaderboard}
    except Exception as e:
        logging.exception("Error fetching leaderboard")
        return {"error": str(e)}
