"""
Face to the Mat - Game Utilities
This module contains utility functions and constants used throughout the game.
"""
import random
import logging
import os
import json
from typing import Dict, List, Tuple, Union, Optional, Callable, Any

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fttm.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("face_to_the_mat")

# Game constants
TV_GRADES = ["AAA", "AA", "A", "B", "C", "D", "E", "F"]
CIRCLE_SPACES = [0, 1, 2, 3, 4, 6, 8, 10]
SQUARE_SPACES = [5, 7, 9, 11, 12, 13, 14]
PIN_SPACES = [12, 13, 14]
FINISHER_SPACE = 15

# TV Grade Kickout Ranges
PIN_RANGES = {
    'AAA': range(11, 44),  # 11-43 inclusive
    'AA': range(11, 37),   # 11-36 inclusive
    'A': range(11, 34),    # 11-33 inclusive
    'B': range(11, 27),    # 11-26 inclusive
    'C': range(11, 24),    # 11-23 inclusive
    'D': range(11, 17),    # 11-16 inclusive
    'E': range(11, 14),    # 11-13 inclusive
    'F': range(11, 12)     # 11 only
}

# Skill types for reference
MENTAL_SKILLS = ["smart", "cheat", "mean"]
PHYSICAL_SKILLS = ["agile", "strong", "powerful", "quick", "heavy"]
SOCIAL_SKILLS = ["favorite", "helped"]
SPECIALTY_SKILLS = ["grudge", "tv", "specialty", "object"]

# Dice rolling functions
def roll_d6() -> int:
    """Roll a single 6-sided die"""
    return random.randint(1, 6)

def roll_d66() -> int:
    """Roll two 6-sided dice and combine for a d66 roll"""
    die_10s = random.randint(1, 6)
    die_1s = random.randint(1, 6)
    return die_10s * 10 + die_1s

def get_pin_range(tv_grade: str) -> range:
    """Get the kickout range for a specific TV grade"""
    return PIN_RANGES.get(tv_grade, range(11, 12))  # Default to F range if not found

def get_space_type(position: int) -> str:
    """Determine the type of a board space based on position"""
    if position == FINISHER_SPACE:
        return "FINISHER"
    elif position in PIN_SPACES:
        return "PIN"
    elif position in SQUARE_SPACES:
        return "SQUARE"
    elif position in CIRCLE_SPACES:
        return "CIRCLE"
    else:
        return "UNKNOWN"

def compare_tv_grades(grade1: str, grade2: str) -> int:
    """
    Compare two TV grades
    Returns:  1 if grade1 is better
              0 if grades are equal
             -1 if grade2 is better
    """
    try:
        index1 = TV_GRADES.index(grade1)
        index2 = TV_GRADES.index(grade2)
        
        if index1 < index2:
            return 1  # Lower index = better grade
        elif index1 > index2:
            return -1
        else:
            return 0
    except ValueError:
        logger.error(f"Invalid TV grade: {grade1} or {grade2}")
        return 0

def format_log_message(message: str, category: str = "INFO") -> str:
    """Format a message for the game log with a category prefix"""
    if category == "INFO":
        return message
    elif category == "ACTION":
        return f"ACTION: {message}"
    elif category == "RESULT":
        return f"RESULT: {message}"
    elif category == "ERROR":
        return f"ERROR: {message}"
    else:
        return message

def save_match_history(match_data: Dict, filename: str = "match_history.json") -> bool:
    """Save match data to a JSON history file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Load existing history if it exists
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                history = json.load(f)
        else:
            history = {"matches": []}
        
        # Add new match data
        history["matches"].append(match_data)
        
        # Save updated history
        with open(filename, 'w') as f:
            json.dump(history, f, indent=2)
        
        return True
    except Exception as e:
        logger.error(f"Error saving match history: {e}")
        return False

# Highlight Reel chart functions
def get_highlight_reel_event(reel_id: str, roll: int) -> str:
    """Get a highlight reel event based on the reel ID and roll"""
    # These will be implemented with actual chart data in the future
    highlight_reels = {
        "G": {
            11: "Gang/group turns on wrestler. Gain +2 Grudge.",
            12: "Gang/group helps wrestler get the win.",
            # Additional entries would go here
        },
        "M": {
            11: "Manager turns on wrestler. Gain +2 Grudge.",
            12: "Manager helps wrestler get the win.",
            # Additional entries would go here
        },
        "V": {
            11: "Valet turns on wrestler. Gain +2 Grudge.",
            12: "Valet helps wrestler get the win.",
            # Additional entries would go here
        },
    }
    
    if reel_id in highlight_reels and roll in highlight_reels[reel_id]:
        return highlight_reels[reel_id][roll]
    
    return f"Highlight Reel {reel_id} event (roll: {roll}). This feature will be implemented in a future update."

# Wild Card chart functions
def get_wild_card_event(card_type: str, roll: int) -> str:
    """Get a wild card event based on the card type and roll"""
    # These will be implemented with actual chart data in the future
    wild_card_events = {
        "Physical": {
            11: "Wrestler injures their opponent. -1 TV for opponent.",
            12: "Wrestler performs an amazing move. +1 TV.",
            # Additional entries would go here
        },
        "Mental": {
            11: "Wrestler outwits their opponent. Score 2 points.",
            12: "Wrestler applies a technical hold. Opponent must roll to escape.",
            # Additional entries would go here
        },
    }
    
    if card_type in wild_card_events and roll in wild_card_events[card_type]:
        return wild_card_events[card_type][roll]
    
    return f"Wild Card {card_type} event (roll: {roll}). This feature will be implemented in a future update."