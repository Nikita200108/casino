import random

class CrashGame:
    def __init__(self):
        self.multiplier = 1.0
    
    def play(self, bet_amount: float, cashout_at: float = None) -> dict:
        crash_point = self.generate_crash_point()
        
        if cashout_at is None:
            cashout_at = random.uniform(1.5, crash_point - 0.5) if crash_point > 2 else crash_point * 0.8
        
        if cashout_at <= crash_point:
            profit = bet_amount * (cashout_at - 1)
            result = 'win'
        else:
            profit = -bet_amount
            result = 'lose'
        
        return {
            'result': result,
            'profit': profit,
            'crash_point': round(crash_point, 2),
            'cashout_at': round(cashout_at, 2),
            'multiplier': round(cashout_at, 2) if result == 'win' else 0
        }
    
    def generate_crash_point(self) -> float:
        e = random.random()
        if e < 0.01:
            return 1.0
        return max(1.01, min(100, 1 / (1 - e) * 0.99))
