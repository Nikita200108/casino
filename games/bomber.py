import random
from typing import List

class BomberGame:
    def __init__(self, grid_size: int = 5, bombs_count: int = 5):
        self.grid_size = grid_size
        self.bombs_count = bombs_count
        self.grid = []
        self.revealed = []
        self.game_over = False
        self.multiplier = 1.0
    
    def initialize_grid(self):
        total_cells = self.grid_size * self.grid_size
        bomb_positions = random.sample(range(total_cells), self.bombs_count)
        
        self.grid = ['safe' if i not in bomb_positions else 'bomb' for i in range(total_cells)]
        self.revealed = [False] * total_cells
        self.game_over = False
        self.multiplier = 1.0
    
    def reveal_cell(self, position: int) -> dict:
        if self.revealed[position]:
            return {'status': 'already_revealed', 'game_over': self.game_over}
        
        self.revealed[position] = True
        
        if self.grid[position] == 'bomb':
            self.game_over = True
            return {
                'status': 'bomb',
                'game_over': True,
                'multiplier': 0
            }
        
        safe_revealed = sum(1 for i, cell in enumerate(self.grid) if cell == 'safe' and self.revealed[i])
        total_safe = sum(1 for cell in self.grid if cell == 'safe')
        
        self.multiplier = 1 + (safe_revealed / total_safe) * 2
        
        return {
            'status': 'safe',
            'game_over': False,
            'multiplier': round(self.multiplier, 2),
            'revealed_count': safe_revealed,
            'total_safe': total_safe
        }
    
    def play(self, bet_amount: float, reveals: int = 5) -> dict:
        self.initialize_grid()
        
        revealed_positions = []
        for _ in range(reveals):
            available = [i for i, r in enumerate(self.revealed) if not r]
            if not available:
                break
            
            position = random.choice(available)
            revealed_positions.append(position)
            result = self.reveal_cell(position)
            
            if result['game_over']:
                return {
                    'result': 'lose',
                    'profit': -bet_amount,
                    'revealed_positions': revealed_positions,
                    'bomb_position': position
                }
        
        profit = bet_amount * (self.multiplier - 1)
        return {
            'result': 'win',
            'profit': profit,
            'multiplier': self.multiplier,
            'revealed_positions': revealed_positions
        }
