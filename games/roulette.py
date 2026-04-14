import random
from typing import Dict

class RouletteGame:
    def __init__(self):
        self.numbers = list(range(0, 37))
        self.red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        self.black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
    
    def spin(self, bet_type: str, bet_value: any, bet_amount: float) -> dict:
        winning_number = random.choice(self.numbers)
        
        is_win = False
        multiplier = 0
        
        if bet_type == 'number':
            if int(bet_value) == winning_number:
                is_win = True
                multiplier = 35
        
        elif bet_type == 'color':
            if bet_value == 'red' and winning_number in self.red_numbers:
                is_win = True
                multiplier = 1
            elif bet_value == 'black' and winning_number in self.black_numbers:
                is_win = True
                multiplier = 1
        
        elif bet_type == 'even_odd':
            if bet_value == 'even' and winning_number != 0 and winning_number % 2 == 0:
                is_win = True
                multiplier = 1
            elif bet_value == 'odd' and winning_number % 2 == 1:
                is_win = True
                multiplier = 1
        
        elif bet_type == 'high_low':
            if bet_value == 'low' and 1 <= winning_number <= 18:
                is_win = True
                multiplier = 1
            elif bet_value == 'high' and 19 <= winning_number <= 36:
                is_win = True
                multiplier = 1
        
        profit = bet_amount * multiplier if is_win else -bet_amount
        
        return {
            'result': 'win' if is_win else 'lose',
            'profit': profit,
            'winning_number': winning_number,
            'bet_type': bet_type,
            'bet_value': bet_value,
            'multiplier': multiplier
        }
