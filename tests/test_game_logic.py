import os
import sys
import pytest

# Add the src directory to the Python path so we can import game_logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from game_logic import Game, Card, Wrestler


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


def test_in_control_requires_skill():
    """A wrestler in control without the card's skill should not move."""
    game = Game()

    # Set up wrestlers
    favored = Wrestler(
        game,
        name="Favored",
        sex="M",
        height=72,
        weight=200,
        hometown="City",
        tv_grade="A",
        grudge_grade=0,
        skills={},
        specialty=None,
        finisher=None,
    )
    underdog = Wrestler(
        game,
        name="Underdog",
        sex="M",
        height=72,
        weight=200,
        hometown="Town",
        tv_grade="A",
        grudge_grade=0,
        skills={"brawling": "square"},
        specialty=None,
        finisher=None,
    )
    game.favored_wrestler = favored
    game.underdog_wrestler = underdog
    game.in_control = favored

    # Deck contains a card the opponent can use if control fails
    follow_up = Card(id=2, control=False, type="Brawling", points=2)
    game.deck = [follow_up]
    game.discard_pile = []

    control_card = Card(id=1, control=True, type="Brawling", points=2)

    game.resolve_card(control_card)

    assert favored.position == 0
    assert underdog.position == 2
