"""
Face to the Mat - Card Manager
This module handles loading, managing, and drawing cards for the game.
"""
import random
import json
import os
import logging
from typing import Dict, List, Union, Optional, Tuple, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_to_the_mat")

class Card:
    """Represents a Fast Action Card (FAC) in the game"""
    def __init__(self, id: int, control: bool, type: str, 
                 points: Union[int, float, str, Dict, None] = None, 
                 text: Optional[str] = None):
        """Initialize a card with its attributes"""
        self.id = id
        self.control = control
        self.type = type
        self.points = points
        self.text = text
        
        # Flag for submission cards based on text content
        self.is_submission = "Submission!" in (text or "")
        
        # Flag for highlight reel & wild card references
        self.is_highlight_reel_ref = "HIGHLIGHT REEL" in (text or "")
        self.is_wild_card = type.lower() == "wild card"

    def get_points(self, tv_grade: Optional[str] = None) -> int:
        """
        Get the points value for this card, considering TV Grade if needed
        """
        if isinstance(self.points, dict) and tv_grade:  # TV card
            return self.points.get(tv_grade, 0)
        elif self.points == "d6":
            return random.randint(1, 6)
        elif isinstance(self.points, (int, float)):
            return int(self.points)
        return 0
    
    def __str__(self) -> str:
        """String representation of the card"""
        return f"Card {self.id}: {self.type} ({'Control' if self.control else 'No Control'})"


class CardManager:
    """Manages the deck of cards, including shuffling, drawing, and reset"""
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the card manager with a deck of cards"""
        self.deck: List[Card] = []
        self.discard_pile: List[Card] = []
        
        if data_path is None:
            # Default path relative to the script location
            self.data_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'gamedata', 'fac_deck.json'
            )
        else:
            self.data_path = data_path
        
        self.load_deck()
        self.shuffle_deck()
    
    def load_deck(self) -> None:
        """Load cards from the JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            self.deck = [Card(**card) for card in data['cards']]
            logger.info(f"Loaded {len(self.deck)} cards from {self.data_path}")
        except FileNotFoundError:
            logger.error(f"Error: fac_deck.json not found at {self.data_path}")
            self.deck = []
        except json.JSONDecodeError:
            logger.error(f"Error: Invalid JSON in fac_deck.json")
            self.deck = []
    
    def shuffle_deck(self) -> None:
        """Shuffle the deck of cards"""
        random.shuffle(self.deck)
        logger.debug("Deck shuffled")
    
    def draw_card(self) -> Optional[Card]:
        """Draw a card from the deck, reshuffling if necessary"""
        if not self.deck:
            if not self.discard_pile:
                logger.error("Error: No cards available even after reshuffling.")
                return None
                
            logger.info("Deck is empty. Reshuffling discard pile.")
            self.deck = self.discard_pile
            self.discard_pile = []
            self.shuffle_deck()
        
        if self.deck:
            card = self.deck.pop(0)
            self.discard_pile.append(card)
            logger.debug(f"Drew card: {card}")
            return card
        else:
            logger.error("Error: No cards available even after reshuffling.")
            return None
    
    def reset(self) -> None:
        """Reset the deck by combining with discard pile and shuffling"""
        self.deck.extend(self.discard_pile)
        self.discard_pile = []
        self.shuffle_deck()
        logger.info("Card deck reset and reshuffled")
    
    def get_card_types(self) -> List[str]:
        """Get a list of unique card types in the whole deck"""
        all_cards = self.deck + self.discard_pile
        return list(set(card.type for card in all_cards))
    
    def get_cards_by_type(self, card_type: str) -> List[Card]:
        """Get all cards of a specific type"""
        all_cards = self.deck + self.discard_pile
        return [card for card in all_cards if card.type.lower() == card_type.lower()]
    
    def get_submission_cards(self) -> List[Card]:
        """Get all submission cards"""
        all_cards = self.deck + self.discard_pile
        return [card for card in all_cards if card.is_submission]
    
    def get_highlight_reel_ref_cards(self) -> List[Card]:
        """Get all cards that reference highlight reels"""
        all_cards = self.deck + self.discard_pile
        return [card for card in all_cards if card.is_highlight_reel_ref]
    
    def get_wild_cards(self) -> List[Card]:
        """Get all wild cards"""
        all_cards = self.deck + self.discard_pile
        return [card for card in all_cards if card.is_wild_card]