from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    RU = "ru"
    EN = "en"

class GameType(str, Enum):
    BLACKJACK = "blackjack"
    ROULETTE = "roulette"
    CRASH = "crash"
    BOMBER = "bomber"
    DICE = "dice"
    SLOTS = "slots"

class PaymentMethod(str, Enum):
    TON = "ton"
    TELEGRAM_STARS = "telegram_stars"
    STRIPE = "stripe"

class User(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    balance: float = 1000.0
    language: Language = Language.EN
    created_at: str

class Transaction(BaseModel):
    user_id: int
    amount: float
    type: str
    payment_method: Optional[str] = None
    status: str = "pending"
    created_at: str

class GameHistory(BaseModel):
    user_id: int
    game_type: GameType
    bet_amount: float
    result: str
    profit: float
    details: dict = {}
    created_at: str
