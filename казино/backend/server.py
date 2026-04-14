from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import uuid

from models import User, Transaction, GameHistory, GameType, PaymentMethod, Language
from games.blackjack import BlackjackGame
from games.roulette import RouletteGame
from games.crash import CrashGame
from games.bomber import BomberGame
from games.dice import DiceGame
from games.slots import SlotsGame

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI(title="Telegram Casino API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UserCreate(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    language: Language = Language.EN


class UserUpdate(BaseModel):
    language: Optional[Language] = None


class PlayGameRequest(BaseModel):
    telegram_id: int
    game_type: GameType
    bet_amount: float
    game_params: Optional[Dict] = {}


class DepositRequest(BaseModel):
    telegram_id: int
    amount: float
    payment_method: PaymentMethod


@api_router.post("/users")
async def create_or_get_user(user_data: UserCreate):
    existing = await db.users.find_one({"telegram_id": user_data.telegram_id}, {"_id": 0})
    
    if existing:
        return existing
    
    user_dict = user_data.model_dump()
    user_dict['balance'] = 1000.0
    user_dict['created_at'] = datetime.now(timezone.utc).isoformat()
    
    await db.users.insert_one(user_dict)
    return user_dict


@api_router.get("/users/{telegram_id}")
async def get_user(telegram_id: int):
    user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@api_router.patch("/users/{telegram_id}")
async def update_user(telegram_id: int, update_data: UserUpdate):
    update_dict = {k: v for k, v in update_data.model_dump().items() if v is not None}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = await db.users.update_one(
        {"telegram_id": telegram_id},
        {"$set": update_dict}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True}


@api_router.post("/games/play")
async def play_game(game_request: PlayGameRequest):
    user = await db.users.find_one({"telegram_id": game_request.telegram_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user['balance'] < game_request.bet_amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    
    game_result = None
    
    if game_request.game_type == GameType.BLACKJACK:
        game = BlackjackGame()
        game_result = game.play(game_request.bet_amount)
    
    elif game_request.game_type == GameType.ROULETTE:
        game = RouletteGame()
        params = game_request.game_params
        game_result = game.spin(
            params.get('bet_type', 'color'),
            params.get('bet_value', 'red'),
            game_request.bet_amount
        )
    
    elif game_request.game_type == GameType.CRASH:
        game = CrashGame()
        game_result = game.play(
            game_request.bet_amount,
            game_request.game_params.get('cashout_at')
        )
    
    elif game_request.game_type == GameType.BOMBER:
        game = BomberGame()
        game_result = game.play(
            game_request.bet_amount,
            game_request.game_params.get('reveals', 5)
        )
    
    elif game_request.game_type == GameType.DICE:
        game = DiceGame()
        params = game_request.game_params
        game_result = game.roll(
            game_request.bet_amount,
            params.get('prediction', 'over'),
            params.get('target_number')
        )
    
    elif game_request.game_type == GameType.SLOTS:
        game = SlotsGame()
        game_result = game.spin(game_request.bet_amount)
    
    new_balance = user['balance'] + game_result['profit']
    
    await db.users.update_one(
        {"telegram_id": game_request.telegram_id},
        {"$set": {"balance": new_balance}}
    )
    
    history_entry = {
        "user_id": game_request.telegram_id,
        "game_type": game_request.game_type.value,
        "bet_amount": game_request.bet_amount,
        "result": game_result['result'],
        "profit": game_result['profit'],
        "details": game_result,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.game_history.insert_one(history_entry)
    
    return {
        "game_result": game_result,
        "new_balance": new_balance,
        "profit": game_result['profit']
    }


@api_router.post("/deposit")
async def deposit(deposit_request: DepositRequest):
    user = await db.users.find_one({"telegram_id": deposit_request.telegram_id}, {"_id": 0})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transaction = {
        "user_id": deposit_request.telegram_id,
        "amount": deposit_request.amount,
        "type": "deposit",
        "payment_method": deposit_request.payment_method.value,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.transactions.insert_one(transaction)
    
    new_balance = user['balance'] + deposit_request.amount
    await db.users.update_one(
        {"telegram_id": deposit_request.telegram_id},
        {"$set": {"balance": new_balance}}
    )
    
    return {
        "success": True,
        "new_balance": new_balance,
        "transaction": transaction
    }


@api_router.get("/transactions/{telegram_id}")
async def get_transactions(telegram_id: int, limit: int = 50):
    transactions = await db.transactions.find(
        {"user_id": telegram_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return transactions


@api_router.get("/history/{telegram_id}")
async def get_game_history(telegram_id: int, limit: int = 50):
    history = await db.game_history.find(
        {"user_id": telegram_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    
    return history


@api_router.get("/")
async def root():
    return {"message": "Telegram Casino API", "version": "1.0.0"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
