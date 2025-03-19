import random
import json
import os
from typing import Dict, List, Union, Optional, Tuple, Any

class Card:
    """
    Represents a Fast Action Card (FAC) in the Face to the Mat game.
    
    Cards determine which moves can be performed and how many points are scored
    during a wrestling match.
    
    Attributes:
        id (int): Unique identifier for the card
        control (bool): Whether this is an "in control" card
        type (str): The card type (e.g., "Agile", "TV", "Grudge", etc.)
        points (Union[int, float, str, Dict]): Points value or dict mapping TV grades to points
        text (Optional[str]): Additional text description or special instructions
        is_submission (bool): Whether this card represents a submission move
    """
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
        """
        Calculate the points value for this card, taking into account TV grade if applicable.
        
        Args:
            tv_grade (Optional[str]): The TV grade to use for TV cards
            
        Returns:
            int: The number of points for this card
        """
        if isinstance(self.points, dict):  # TV card
            return self.points.get(tv_grade, 0)
        elif self.points == "d6":
            return random.randint(1, 6)
        elif isinstance(self.points, (int, float)):
            return int(self.points)
        return 0
    
    def __str__(self) -> str:
        """String representation of the card."""
        return f"Card {self.id}: {self.type} ({'Control' if self.control else 'No Control'})"


class CardManager:
    """
    Manages the deck of Fast Action Cards (FACs) for the Face to the Mat game.
    
    This class handles loading, shuffling, drawing, and managing the discard pile
    for the card deck.
    
    Attributes:
        deck (List[Card]): The current deck of cards
        discard_pile (List[Card]): Cards that have been played
        data_path (str): Path to the card data file
    """
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the CardManager with an empty deck and discard pile.
        
        Args:
            data_path (Optional[str]): Path to the card data file. If None, uses default path.
        """
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
        """
        Load the card deck from the JSON file.
        
        Raises:
            FileNotFoundError: If the deck file is not found
            json.JSONDecodeError: If the deck file contains invalid JSON
        """
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
        """Shuffle the current deck of cards."""
        random.shuffle(self.deck)
    
    def draw_card(self) -> Optional[Card]:
        """
        Draw a card from the deck. If the deck is empty, shuffle the discard pile
        back into the deck.
        
        Returns:
            Optional[Card]: The drawn card, or None if no cards are available
        """
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
        """Reset the card manager by returning all cards to the deck and shuffling."""
        self.deck.extend(self.discard_pile)
        self.discard_pile = []
        self.shuffle_deck()
    
    def get_card_types(self) -> List[str]:
        """
        Get a list of all unique card types in the deck.
        
        Returns:
            List[str]: A list of card types
        """
        all_cards = self.deck + self.discard_pile
        return list(set(card.type for card in all_cards))
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """
        Get all cards of a specific type.
        
        Args:
            card_type (str): The type of card to find
            
        Returns:
            List[Card]: A list of cards matching the specified type
        """
        all_cards = self.deck + self.discard_pile
        return [card for card in all_cards if card.type.lower() == card_type.lower()]


# Functions for specific card type resolution

def resolve_submission_card(card: Card, wrestler, opponent, d6_func=None) -> str:
    """
    Resolve a submission card, which can score multiple points until the hold is broken.
    
    Args:
        card (Card): The submission card being played
        wrestler: The wrestler performing the submission
        opponent: The wrestler defending against the submission
        d6_func (callable, optional): Function to roll a d6. Used for testing.
        
    Returns:
        str: A description of what happened
    """
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
    """
    Resolve a Test of Strength card, which is a special type of contest between wrestlers.
    
    Args:
        card (Card): The Test of Strength card being played
        face_wrestler: The face (good guy) wrestler
        heel_wrestler: The heel (bad guy) wrestler
        d6_func (callable, optional): Function to roll a d6. Used for testing.
        
    Returns:
        str: A description of what happened
    """
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
    """
    Resolve a Helped card, which involves outside help from an ally.
    
    Args:
        card (Card): The Helped card being played
        wrestler: The wrestler receiving help
        ally: The wrestler providing the help (optional)
        
    Returns:
        str: A description of what happened
    """
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