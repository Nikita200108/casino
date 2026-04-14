import random

class DiceGame:
    def __init__(self):
        self.dice_faces = [1, 2, 3, 4, 5, 6]
    
    def roll(self, bet_amount: float, prediction: str, target_number: int = None) -> dict:
        dice1 = random.choice(self.dice_faces)
        dice2 = random.choice(self.dice_faces)
        total = dice1 + dice2
        
        is_win = False
        multiplier = 0
        
        if prediction == 'over':
            threshold = target_number or 7
            if total > threshold:
                is_win = True
                multiplier = 1.5
        
        elif prediction == 'under':
            threshold = target_number or 7
            if total < threshold:
                is_win = True
                multiplier = 1.5
        
        elif prediction == 'exact':
            if total == target_number:
                is_win = True
                multiplier = 5
        
        elif prediction == 'even':
            if total % 2 == 0:
                is_win = True
                multiplier = 1
        
        elif prediction == 'odd':
            if total % 2 == 1:
                is_win = True
                multiplier = 1
        
        profit = bet_amount * multiplier if is_win else -bet_amount
        
        return {
            'result': 'win' if is_win else 'lose',
            'profit': profit,
            'dice1': dice1,
            'dice2': dice2,
            'total': total,
            'prediction': prediction,
            'target_number': target_number,
            'multiplier': multiplier
        }
