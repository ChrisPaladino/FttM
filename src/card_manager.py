import random
import json
import os
from typing import Dict, List, Union, Optional, Tuple, Any

class Card:
    def __init__(self, id: int, control: bool, type: str, 
                 points: Union[int, float, str, Dict, None] = None, 
                 text: Optional[str] = None):
        self.id = id
        self.control = control
        self.type = type
        self.points = points
        self.text = text
        self.is_submission = "Submission!" in (text or "")

    def get_points(self, tv_grade: Optional[str] = None) -> int:
        if isinstance(self.points, dict):  # TV card
            return self.points.get(tv_grade, 0)
        elif self.points == "d6":
            return random.randint(1, 6)
        elif isinstance(self.points, (int, float)):
            return int(self.points)
        return 0
    
    def __str__(self) -> str:
        return f"Card {self.id}: {self.type} ({'Control' if self.control else 'No Control'})"


class CardManager:
    def __init__(self, data_path: Optional[str] = None):
        self.deck: List[Card] = []
        self.discard_pile: List[Card] = []
        
        if data_path is None:
            # Default path relative to the script location
            self.data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gamedata', 'fac_deck.json')
        else:
            self.data_path = data_path
        
        self.load_deck()
        self.shuffle_deck()
    
    def load_deck(self) -> None:
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            self.deck = [Card(**card) for card in data['cards']]
        except FileNotFoundError:
            print(f"Error: fac_deck.json not found at {self.data_path}")
            self.deck = []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in fac_deck.json")
            self.deck = []
    
    def shuffle_deck(self) -> None:
        random.shuffle(self.deck)
    
    def draw_card(self) -> Optional[Card]:
        if not self.deck:
            if not self.discard_pile:
                print("Error: No cards available even after reshuffling.")
                return None
                
            print("Deck is empty. Reshuffling discard pile.")
            self.deck = self.discard_pile
            self.discard_pile = []
            self.shuffle_deck()
        
        if self.deck:
            card = self.deck.pop(0)
            self.discard_pile.append(card)
            return card
        else:
            print("Error: No cards available even after reshuffling.")
            return None
    
    def reset(self) -> None:
        self.deck.extend(self.discard_pile)
        self.discard_pile = []
        self.shuffle_deck()
    
    def get_card_types(self) -> List[str]:
        all_cards = self.deck + self.discard_pile
        return list(set(card.type for card in all_cards))
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        all_cards = self.deck + self.discard_pile
        return [card for card in all_cards if card.type.lower() == card_type.lower()]