import unittest
import os
import json
import tempfile
from typing import Dict, List, Optional, Any, Tuple
import random

# Mock classes for testing
class MockCard:
    """Mock Card class for testing."""
    def __init__(self, id=1, control=False, type="Test", points=1, text=None):
        self.id = id
        self.control = control
        self.type = type
        self.points = points
        self.text = text
        self.is_submission = "Submission!" in (text or "")
    
    def get_points(self, tv_grade=None):
        if isinstance(self.points, dict):
            return self.points.get(tv_grade, 0)
        elif self.points == "d6":
            return random.randint(1, 6)
        elif isinstance(self.points, (int, float)):
            return int(self.points)
        return 0
    
    def __str__(self):
        return f"Card {self.id}: {self.type} ({'Control' if self.control else 'No Control'})"


class MockWrestler:
    """Mock Wrestler class for testing."""
    def __init__(self, name="Test Wrestler", tv_grade="C", grudge_grade=0, skills=None, 
                 specialty=None, finisher=None, position=0):
        self.name = name
        self.tv_grade = tv_grade
        self.grudge_grade = grudge_grade
        self.skills = skills or {"test": "star"}
        self.specialty = specialty or {"name": "Test Move", "points": 3}
        self.finisher = finisher or {"name": "Test Finisher", "range": (11, 33)}
        self.position = position
        self.last_card_scored = False
        self.allies = []
        self.rivals = []
    
    def can_use_skill(self, skill, position):
        skill = skill.lower()
        if skill in ["tv", "grudge", "specialty"]:
            return True
        if skill in self.skills:
            skill_type = self.skills[skill]
            if position == 15:
                return True
            elif skill_type == 'star':
                return True
            elif skill_type == 'square' and position in [5, 7, 9, 11, 12, 13, 14]:
                return True
            elif skill_type == 'circle' and position in [0, 1, 2, 3, 4, 6, 8, 10]:
                return True
        return False
    
    def has_skill(self, skill):
        return skill.lower() in self.skills
    
    def has_specialty(self):
        return bool(self.specialty and self.specialty.get('name') and self.specialty.get('points'))
    
    def is_trailing(self, opponent):
        return self.position < opponent.position
    
    def score(self, points):
        self.position += points
        self.position = min(self.position, 15)
        self.last_card_scored = True


def create_test_data_file(data: Dict, prefix: str = "test_") -> str:
    """
    Create a temporary JSON file with test data.
    
    Args:
        data: Dictionary to save as JSON
        prefix: Prefix for the temporary file name
    
    Returns:
        str: Path to the created file
    """
    with tempfile.NamedTemporaryFile(prefix=prefix, suffix=".json", delete=False, mode="w") as f:
        json.dump(data, f)
        return f.name


def create_test_wrestlers_file() -> str:
    """
    Create a temporary wrestlers.json file for testing.
    
    Returns:
        str: Path to the created file
    """
    test_wrestlers = {
        "wrestlers": [
            {
                "name": "Test Face",
                "sex": "Male",
                "height": "6'0\"",
                "weight": "220",
                "hometown": "Test City",
                "tv_grade": "B",
                "grudge_grade": 2,
                "skills": {
                    "agile": "star",
                    "strong": "star",
                    "smart": "square"
                },
                "specialty": {
                    "name": "Test Special",
                    "points": 3
                },
                "finisher": {
                    "name": "Test Finisher",
                    "range": [11, 33]
                }
            },
            {
                "name": "Test Heel",
                "sex": "Male",
                "height": "6'2\"",
                "weight": "240",
                "hometown": "Villain Town",
                "tv_grade": "C",
                "grudge_grade": 4,
                "skills": {
                    "powerful": "star",
                    "mean": "star",
                    "cheat": "square"
                },
                "specialty": {
                    "name": "Villain Move",
                    "points": 2
                },
                "finisher": {
                    "name": "Villain Finisher",
                    "range": [11, 30]
                }
            }
        ]
    }
    return create_test_data_file(test_wrestlers, prefix="test_wrestlers_")


def create_test_cards_file() -> str:
    """
    Create a temporary cards.json file for testing.
    
    Returns:
        str: Path to the created file
    """
    test_cards = {
        "cards": [
            {
                "id": 1,
                "control": False,
                "type": "Agile",
                "points": 1
            },
            {
                "id": 2,
                "control": True,
                "type": "Strong",
                "points": 2
            },
            {
                "id": 3,
                "control": False,
                "type": "TV",
                "points": {
                    "AAA": 5,
                    "AA": 4,
                    "A": 3,
                    "B": 2,
                    "C": 1,
                    "D": 0,
                    "E": 0,
                    "F": 0
                }
            },
            {
                "id": 4,
                "control": False,
                "type": "Grudge",
                "points": 2
            },
            {
                "id": 5,
                "control": False,
                "type": "Specialty",
                "text": "Check wrestler's card."
            }
        ]
    }
    return create_test_data_file(test_cards, prefix="test_cards_")


def cleanup_test_files(file_paths: List[str]) -> None:
    """
    Delete temporary test files.
    
    Args:
        file_paths: List of file paths to delete
    """
    for path in file_paths:
        try:
            os.remove(path)
        except Exception as e:
            print(f"Error deleting test file {path}: {e}")


# Test base class
class FTTMTestCase(unittest.TestCase):
    """Base test case class for Face to the Mat tests."""
    
    def setUp(self):
        """Set up test case with temporary test files."""
        self.test_files = []
        self.wrestlers_file = create_test_wrestlers_file()
        self.cards_file = create_test_cards_file()
        self.test_files.extend([self.wrestlers_file, self.cards_file])
    
    def tearDown(self):
        """Clean up temporary test files."""
        cleanup_test_files(self.test_files)
    
    def create_mock_game(self):
        """Create a minimal mock game object for testing."""
        from src.game_utilities import roll_d6, roll_d66
        
        # A simple mock game class that has the minimum needed for tests
        class MockGame:
            def __init__(self):
                self.favored_wrestler = MockWrestler(name="Test Face", tv_grade="B", grudge_grade=2)
                self.underdog_wrestler = MockWrestler(name="Test Heel", tv_grade="C", grudge_grade=4)
                self.in_control = None
                self.current_card = None
                self.game_over = False
            
            def roll_d6(self):
                return roll_d6()
            
            def roll_d66(self):
                return roll_d66()
                
        return MockGame()


# Helper functions for assertions
def assert_wrestler_position(test_case, wrestler, expected_position, msg=None):
    """
    Assert that a wrestler is at the expected position.
    
    Args:
        test_case: The unittest.TestCase instance
        wrestler: The wrestler to check
        expected_position: The expected position value
        msg: Optional message for the assertion
    """
    test_case.assertEqual(
        wrestler.position, 
        expected_position, 
        msg or f"Expected {wrestler.name} to be at position {expected_position}, but was at {wrestler.position}"
    )


def assert_in_control(test_case, game, expected_wrestler, msg=None):
    """
    Assert that the expected wrestler is in control.
    
    Args:
        test_case: The unittest.TestCase instance
        game: The game instance
        expected_wrestler: The wrestler expected to be in control, or None
        msg: Optional message for the assertion
    """
    if expected_wrestler is None:
        test_case.assertIsNone(
            game.in_control,
            msg or "Expected no wrestler to be in control"
        )
    else:
        test_case.assertIs(
            game.in_control,
            expected_wrestler,
            msg or f"Expected {expected_wrestler.name} to be in control"
        )


if __name__ == "__main__":
    unittest.main()