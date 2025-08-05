import os
import sys
import pytest

# Add the src directory to the Python path so we can import game_logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from game_logic import Game


@pytest.fixture
def game():
    """Return a new Game instance for each test."""
    return Game()


@pytest.mark.parametrize(
    "grade, expected",
    [
        ("AAA", range(11, 44)),
        ("AA", range(11, 37)),
        ("A", range(11, 34)),
        ("B", range(11, 27)),
        ("C", range(11, 24)),
        ("D", range(11, 17)),
        ("E", range(11, 14)),
        ("F", range(11, 12)),
    ],
)
def test_get_pin_range_known_grades(game, grade, expected):
    """The pin range should match the predefined ranges for each grade."""
    assert game.get_pin_range(grade) == expected


def test_get_pin_range_unknown_grade(game):
    """Unknown grades should default to the F range (11)."""
    assert game.get_pin_range("UNKNOWN") == range(11, 12)
