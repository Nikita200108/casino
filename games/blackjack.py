import random
from typing import List, Tuple

class BlackjackGame:
    def __init__(self):
        self.deck = []
        self.player_hand = []
        self.dealer_hand = []
        self.reset_deck()
    
    def reset_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.deck = [{'suit': s, 'value': v} for s in suits for v in values]
        random.shuffle(self.deck)
    
    def calculate_hand_value(self, hand: List[dict]) -> int:
        value = 0
        aces = 0
        
        for card in hand:
            if card['value'] in ['J', 'Q', 'K']:
                value += 10
            elif card['value'] == 'A':
                aces += 1
                value += 11
            else:
                value += int(card['value'])
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def deal_card(self) -> dict:
        if len(self.deck) < 10:
            self.reset_deck()
        return self.deck.pop()
    
    def play(self, bet_amount: float) -> dict:
        self.player_hand = [self.deal_card(), self.deal_card()]
        self.dealer_hand = [self.deal_card(), self.deal_card()]
        
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        while dealer_value < 17:
            self.dealer_hand.append(self.deal_card())
            dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        result = self.determine_winner(player_value, dealer_value)
        
        if result == 'win':
            profit = bet_amount
            if player_value == 21 and len(self.player_hand) == 2:
                profit = bet_amount * 1.5
        elif result == 'push':
            profit = 0
        else:
            profit = -bet_amount
        
        return {
            'result': result,
            'profit': profit,
            'player_hand': self.player_hand,
            'dealer_hand': self.dealer_hand,
            'player_value': player_value,
            'dealer_value': dealer_value
        }
    
    def determine_winner(self, player_value: int, dealer_value: int) -> str:
        if player_value > 21:
            return 'lose'
        if dealer_value > 21:
            return 'win'
        if player_value > dealer_value:
            return 'win'
        elif player_value == dealer_value:
            return 'push'
        else:
            return 'lose'
