import random
from typing import List

class SlotsGame:
    def __init__(self):
        self.symbols = ['🍒', '🍋', '🍊', '🍇', '🔔', '💎', '7️⃣']
        self.symbol_weights = [20, 20, 15, 15, 10, 8, 2]
    
    def spin(self, bet_amount: float) -> dict:
        reel1 = random.choices(self.symbols, weights=self.symbol_weights, k=3)
        reel2 = random.choices(self.symbols, weights=self.symbol_weights, k=3)
        reel3 = random.choices(self.symbols, weights=self.symbol_weights, k=3)
        
        reels = [reel1, reel2, reel3]
        
        result = self.check_win(reels)
        profit = bet_amount * (result['multiplier'] - 1) if result['is_win'] else -bet_amount
        
        return {
            'result': 'win' if result['is_win'] else 'lose',
            'profit': profit,
            'reels': reels,
            'multiplier': result['multiplier'],
            'win_lines': result.get('win_lines', [])
        }
    
    def check_win(self, reels: List[List[str]]) -> dict:
        multiplier = 0
        win_lines = []
        
        for row in range(3):
            line = [reels[0][row], reels[1][row], reels[2][row]]
            
            if line[0] == line[1] == line[2]:
                symbol = line[0]
                if symbol == '7️⃣':
                    multiplier += 50
                elif symbol == '💎':
                    multiplier += 20
                elif symbol == '🔔':
                    multiplier += 10
                elif symbol in ['🍇', '🍊']:
                    multiplier += 5
                else:
                    multiplier += 3
                
                win_lines.append({'row': row, 'symbols': line, 'type': 'full_line'})
            
            elif line[0] == line[1] or line[1] == line[2]:
                multiplier += 1
                win_lines.append({'row': row, 'symbols': line, 'type': 'partial'})
        
        return {
            'is_win': multiplier > 0,
            'multiplier': multiplier,
            'win_lines': win_lines
        }
