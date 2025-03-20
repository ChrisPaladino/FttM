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


# Functions for specific card type resolution

def resolve_submission_card(card: Card, wrestler, opponent, d6_func=None) -> str:
    if d6_func is None:
        d6_func = lambda: random.randint(1, 6)
        
    result = f"{wrestler.name} attempts a submission move!\n"
    points_scored = card.get_points(wrestler.tv_grade)
    wrestler.score(points_scored)
    result += f"{wrestler.name} scores {points_scored} point(s). Position: {wrestler.position}\n"
    
    opponent_is_strong = opponent.has_skill('strong') or opponent.has_skill('powerful')
    
    while True:
        roll = d6_func()
        break_hold = 3 if not opponent_is_strong else 4
        if roll <= break_hold:
            result += f"{opponent.name} breaks the hold with a roll of {roll}.\n"
            break
        else:
            wrestler.score(1)
            result += f"{wrestler.name} scores an additional point. Position: {wrestler.position}\n"
    
    return result

def resolve_test_of_strength(card: Card, face_wrestler, heel_wrestler, d6_func=None) -> str:
    if d6_func is None:
        d6_func = lambda: random.randint(1, 6)
        
    # Check if both wrestlers are strong/powerful
    face_qualified = face_wrestler.has_skill('strong') or face_wrestler.has_skill('powerful')
    heel_qualified = heel_wrestler.has_skill('strong') or heel_wrestler.has_skill('powerful')
    
    result = "Test of Strength card drawn.\n"
    
    if not (face_qualified and heel_qualified):
        return result + "Both wrestlers must have STRONG or POWERFUL skills. No points scored."
    
    result += "Both wrestlers qualify for Test of Strength.\n"
    
    # Roll until ref breaks
    while True:
        roll = d6_func()
        result += f"Test of Strength roll: {roll}\n"
        
        if roll <= 2:
            face_wrestler.score(1)
            result += f"{face_wrestler.name} wins the exchange and scores 1 point. Position: {face_wrestler.position}\n"
        elif roll <= 4:
            result += "Referee breaks up the Test of Strength. No points scored.\n"
            break
        else:  # 5-6
            heel_wrestler.score(1)
            result += f"{heel_wrestler.name} wins the exchange and scores 1 point. Position: {heel_wrestler.position}\n"
        
        # Check if ref breaks after scoring
        break_roll = d6_func()
        if break_roll <= 4:
            result += f"Referee breaks up the Test of Strength (roll: {break_roll}).\n"
            break
    
    return result

def resolve_helped_card(card: Card, wrestler, ally=None) -> str:
    result = f"{wrestler.name} receives outside help"
    
    if ally:
        result += f" from {ally.name}"
    
    if card.points:
        points = card.get_points(wrestler.tv_grade)
        wrestler.score(points)
        result += f". They score {points} points and move to position {wrestler.position}."
    elif card.text:
        # Special help type that requires Highlight Reel reference
        if "HIGHLIGHT REEL" in card.text:
            result += ".\n" + card.text
            # Here we would implement a call to the Highlight Reel chart
            # This will be implemented in future updates
    else:
        result += ", but it had no effect."
    
    return result