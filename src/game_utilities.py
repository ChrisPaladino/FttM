import random
import logging
from typing import Dict, List, Tuple, Union, Optional, Callable

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

# Dice rolling functions
def roll_d6() -> int:
    return random.randint(1, 6)

def roll_d66() -> int:
    die_10s = random.randint(1, 6)
    die_1s = random.randint(1, 6)
    return die_10s * 10 + die_1s

def get_pin_range(tv_grade: str) -> range:
    return PIN_RANGES.get(tv_grade, range(11, 12))  # Default to F range if not found

def get_space_type(position: int) -> str:
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
    import json
    import os
    
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

# Highlight Reel chart references (stubs for now)
# These will be implemented with actual charts in the future
def get_highlight_reel_event(reel_id: str, roll: int) -> str:
    # This is a stub - will be implemented with actual charts
    return f"Highlight Reel {reel_id} event (roll: {roll}). This feature will be implemented in a future update."

# Wild Card chart references (stubs for now)
def get_wild_card_event(card_type: str, roll: int) -> str:
    # This is a stub - will be implemented with actual charts
    return f"Wild Card {card_type} event (roll: {roll}). This feature will be implemented in a future update."