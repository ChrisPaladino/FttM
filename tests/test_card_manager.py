import unittest
import os
import sys
import json
from typing import List, Dict, Optional

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.card_manager import Card, CardManager
from tests.test_utilities import create_test_cards_file, cleanup_test_files, FTTMTestCase

class CardTest(unittest.TestCase):
    """Tests for the Card class."""
    
    def test_card_initialization(self):
        """Test that a Card can be initialized with various parameter types."""
        # Test with basic parameters
        card1 = Card(id=1, control=False, type="Agile", points=2)
        self.assertEqual(card1.id, 1)
        self.assertEqual(card1.type, "Agile")
        self.assertEqual(card1.points, 2)
        self.assertFalse(card1.control)
        self.assertFalse(card1.is_submission)
        
        # Test with dictionary points
        tv_points = {"AAA": 5, "AA": 4, "A": 3, "B": 2, "C": 1}
        card2 = Card(id=2, control=True, type="TV", points=tv_points)
        self.assertEqual(card2.points, tv_points)
        self.assertTrue(card2.control)
        
        # Test with submission text
        card3 = Card(id=3, control=False, type="Strong", points=1, 
                     text="Submission! Wrestler scores 1 point...")
        self.assertTrue(card3.is_submission)
    
    def test_get_points(self):
        """Test the get_points method with different point types."""
        # Test with fixed points
        card1 = Card(id=1, control=False, type="Agile", points=3)
        self.assertEqual(card1.get_points(), 3)
        
        # Test with TV grade-based points
        tv_points = {"AAA": 5, "AA": 4, "A": 3, "B": 2, "C": 1}
        card2 = Card(id=2, control=True, type="TV", points=tv_points)
        self.assertEqual(card2.get_points("AAA"), 5)
        self.assertEqual(card2.get_points("C"), 1)
        self.assertEqual(card2.get_points("F"), 0)  # Not in dictionary
        
        # Test with d6 points
        card3 = Card(id=3, control=False, type="Powerful", points="d6")
        for _ in range(20):  # Test multiple times for randomness
            points = card3.get_points()
            self.assertGreaterEqual(points, 1)
            self.assertLessEqual(points, 6)


class CardManagerTest(FTTMTestCase):
    """Tests for the CardManager class."""
    
    def test_load_deck(self):
        """Test loading cards from a JSON file."""
        card_manager = CardManager(data_path=self.cards_file)
        
        # Check that cards were loaded
        self.assertGreater(len(card_manager.deck), 0)
        
        # Verify the first card
        with open(self.cards_file, 'r') as f:
            data = json.load(f)
        
        first_card_data = data['cards'][0]
        first_card = card_manager.deck[0]
        
        self.assertEqual(first_card.id, first_card_data['id'])
        self.assertEqual(first_card.type, first_card_data['type'])
        self.assertEqual(first_card.control, first_card_data['control'])
        self.assertEqual(first_card.points, first_card_data['points'])
    
    def test_draw_card(self):
        """Test drawing cards from the deck."""
        card_manager = CardManager(data_path=self.cards_file)
        original_deck_size = len(card_manager.deck)
        
        # Draw a card
        card = card_manager.draw_card()
        
        # Check deck size decreased and discard pile increased
        self.assertEqual(len(card_manager.deck), original_deck_size - 1)
        self.assertEqual(len(card_manager.discard_pile), 1)
        
        # Draw all remaining cards
        for _ in range(original_deck_size - 1):
            card_manager.draw_card()
        
        # Deck should be empty, discard pile full
        self.assertEqual(len(card_manager.deck), 0)
        self.assertEqual(len(card_manager.discard_pile), original_deck_size)
        
        # Drawing one more should reshuffle
        card_manager.draw_card()
        self.assertEqual(len(card_manager.deck), original_deck_size - 1)
        self.assertEqual(len(card_manager.discard_pile), 1)
    
    def test_reset(self):
        """Test resetting the card manager."""
        card_manager = CardManager(data_path=self.cards_file)
        original_deck_size = len(card_manager.deck)
        
        # Draw some cards
        for _ in range(3):
            card_manager.draw_card()
        
        # Reset
        card_manager.reset()
        
        # Deck should be full again, discard empty
        self.assertEqual(len(card_manager.deck), original_deck_size)
        self.assertEqual(len(card_manager.discard_pile), 0)
    
    def test_get_card_types(self):
        """Test getting unique card types."""
        card_manager = CardManager(data_path=self.cards_file)
        
        # Get card types
        card_types = card_manager.get_card_types()
        
        # Check expected types are present (based on test data)
        expected_types = {"Agile", "Strong", "TV", "Grudge", "Specialty"}
        self.assertEqual(set(card_types), expected_types)
    
    def test_get_cards_by_type(self):
        """Test filtering cards by type."""
        card_manager = CardManager(data_path=self.cards_file)
        
        # Get cards of a specific type
        agile_cards = card_manager.get_cards_by_type("Agile")
        
        # Check all returned cards are the right type
        for card in agile_cards:
            self.assertEqual(card.type, "Agile")
        
        # Check count matches expected
        with open(self.cards_file, 'r') as f:
            data = json.load(f)
        
        expected_count = sum(1 for card in data['cards'] if card['type'] == "Agile")
        self.assertEqual(len(agile_cards), expected_count)


# Helper functions for card-related tests
def create_submission_card() -> Card:
    """Create a test submission card."""
    return Card(
        id=57, 
        control=False, 
        type="Strong", 
        points=1,
        text="Submission! Wrestler scores 1 point and additional point(s) until opponent breaks hold with a die roll of 1-3. (Strong opponent, 1-4)"
    )

def create_test_of_strength_card() -> Card:
    """Create a test Test of Strength card."""
    return Card(
        id=56, 
        control=False, 
        type="Test of Strength", 
        text="If BOTH wrestlers are STRONG and/or POWERFUL, roll a die until ref break... 1-2 Face scores 1 point, 3-4 Ref breaks hold, 5-6 Heel scores 1 point"
    )

def create_helped_card_with_points() -> Card:
    """Create a test Helped card with points."""
    return Card(
        id=36, 
        control=True, 
        type="Helped", 
        points=3
    )

def create_helped_card_with_text() -> Card:
    """Create a test Helped card with text but no points."""
    return Card(
        id=38, 
        control=False, 
        type="Helped", 
        text="Go to HIGHLIGHT REEL \"G\", \"M\" or \"V\" depending on the source of help."
    )


# Run the tests
if __name__ == "__main__":
    unittest.main()