"""
Face to the Mat - Wrestler Manager
This module handles wrestler data loading, saving, and management.
"""
import json
import os
import logging
from typing import Dict, List, Union, Optional, Tuple, Any

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("face_to_the_mat")

class Wrestler:
    """Represents a wrestler with all their attributes and state"""
    
    def __init__(self, name: str, sex: str, height: str, weight: str, hometown: str,
                 tv_grade: str, grudge_grade: Union[int, str], skills: Dict[str, str],
                 specialty: Optional[Dict] = None, finisher: Optional[Dict] = None,
                 image: str = "placeholder.png", allies: Optional[List[str]] = None,
                 rivals: Optional[List[str]] = None):
        """Initialize a wrestler with their attributes"""
        self.name = name
        self.sex = sex
        self.height = height
        self.weight = weight
        self.hometown = hometown
        self.tv_grade = tv_grade
        
        # Convert grudge_grade to int if it's a string
        if isinstance(grudge_grade, str):
            try:
                self.grudge_grade = int(grudge_grade)
            except ValueError:
                self.grudge_grade = 0
        else:
            self.grudge_grade = int(grudge_grade)
        
        # Convert skills to lowercase for consistency
        self.skills = {k.lower(): v.lower() for k, v in skills.items()}
        
        # Process specialty move
        self.specialty = specialty or {}
        if self.specialty and 'points' in self.specialty:
            try:
                self.specialty['points'] = int(self.specialty['points'])
            except ValueError:
                self.specialty['points'] = 0
        
        # Process finisher move
        self.finisher = finisher or {}
        if self.finisher and 'range' in self.finisher:
            if isinstance(self.finisher['range'], list):
                self.finisher['range'] = tuple(self.finisher['range'])
            elif isinstance(self.finisher['range'], str):
                try:
                    parts = str(self.finisher['range']).split('-')
                    self.finisher['range'] = (int(parts[0]), int(parts[1]))
                except (ValueError, AttributeError):
                    self.finisher['range'] = (11, 33)  # Default range if parsing fails
        
        # Match tracking attributes
        self.image = image
        self.position = 0
        self.last_card_scored = False
        self.is_title_holder = False
        
        # Initialize allies and rivals
        self.allies = allies or []
        self.rivals = rivals or []

    def can_use_skill(self, skill: str, position: int) -> bool:
        """
        Determine if the wrestler can use a specific skill at their current position
        """
        skill = skill.lower()
        
        # Special skills that can always be used
        if skill in ["tv", "grudge", "specialty"]:
            return True
            
        if skill in self.skills:
            skill_type = self.skills[skill]
            
            # FINISHER space, all skills can be used
            if position == 15:
                return True
            # STAR skills can be used anywhere
            elif skill_type == 'star':
                return True
            # SQUARE skills can only be used on square spaces
            elif skill_type == 'square' and position in [5, 7, 9, 11, 12, 13, 14]:
                return True
            # CIRCLE skills can only be used on circle spaces
            elif skill_type == 'circle' and position in [0, 1, 2, 3, 4, 6, 8, 10]:
                return True
                
        return False

    def has_skill(self, skill: str) -> bool:
        """Check if the wrestler has a specific skill"""
        return skill.lower() in self.skills

    def has_specialty(self) -> bool:
        """Check if the wrestler has a specialty move defined"""
        return bool(self.specialty and self.specialty.get('name') and self.specialty.get('points'))

    def is_trailing(self, opponent) -> bool:
        """Check if this wrestler is trailing behind the opponent"""
        return self.position < opponent.position

    def score(self, points: int) -> None:
        """Update wrestler position by adding points"""
        self.position += points
        self.position = min(self.position, 15)  # Ensure position doesn't exceed 15
        self.last_card_scored = True

    @property
    def specialty_points(self) -> int:
        """Get the points value for this wrestler's specialty move"""
        return int(self.specialty.get('points', 0))

    def add_ally(self, ally_name: str) -> None:
        """Add a wrestler as an ally"""
        if ally_name not in self.allies and ally_name != self.name:
            self.allies.append(ally_name)

    def add_rival(self, rival_name: str) -> None:
        """Add a wrestler as a rival"""
        if rival_name not in self.rivals and rival_name != self.name:
            self.rivals.append(rival_name)

    def remove_ally(self, ally_name: str) -> None:
        """Remove a wrestler from allies"""
        if ally_name in self.allies:
            self.allies.remove(ally_name)

    def remove_rival(self, rival_name: str) -> None:
        """Remove a wrestler from rivals"""
        if rival_name in self.rivals:
            self.rivals.remove(rival_name)
    
    def to_dict(self) -> Dict:
        """Convert wrestler object to dictionary for serialization"""
        wrestler_dict = {
            "name": self.name,
            "sex": self.sex,
            "height": self.height,
            "weight": self.weight,
            "hometown": self.hometown,
            "tv_grade": self.tv_grade,
            "grudge_grade": self.grudge_grade,
            "skills": self.skills,
            "specialty": self.specialty,
            "finisher": self.finisher,
            "image": self.image,
            "allies": self.allies,
            "rivals": self.rivals
        }
        
        # Convert finisher range to list for JSON serialization
        if "finisher" in wrestler_dict and wrestler_dict["finisher"] and "range" in wrestler_dict["finisher"]:
            if isinstance(wrestler_dict["finisher"]["range"], tuple):
                wrestler_dict["finisher"]["range"] = list(wrestler_dict["finisher"]["range"])
                
        return wrestler_dict


class WrestlerManager:
    """Manages the collection of wrestlers, handling loading and saving"""
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the wrestler manager"""
        self.wrestlers: List[Wrestler] = []
        
        if data_path is None:
            # Default path relative to the script location
            self.data_path = os.path.join(
                os.path.dirname(__file__), '..', 'data', 'wrestlers', 'wrestlers.json'
            )
        else:
            self.data_path = data_path
        
        self.load_wrestlers()
    
    def load_wrestlers(self) -> None:
        """Load wrestlers from the JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            self.wrestlers = []
            for w in data['wrestlers']:
                # Handle allies and rivals if they exist in the data
                allies = w.pop('allies', []) if 'allies' in w else []
                rivals = w.pop('rivals', []) if 'rivals' in w else []
                
                wrestler = Wrestler(allies=allies, rivals=rivals, **w)
                self.wrestlers.append(wrestler)
                
            logger.info(f"Loaded {len(self.wrestlers)} wrestlers from {self.data_path}")
        except FileNotFoundError:
            logger.error(f"Error: wrestlers.json not found at {self.data_path}")
            self.wrestlers = []
        except json.JSONDecodeError:
            logger.error(f"Error: Invalid JSON in wrestlers.json")
            self.wrestlers = []
    
    def save_wrestlers(self) -> None:
        """Save all wrestlers to the JSON file"""
        data = {"wrestlers": [w.to_dict() for w in self.wrestlers]}
        
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(self.wrestlers)} wrestlers to {self.data_path}")
    
    def add_wrestler(self, wrestler: Wrestler) -> None:
        """Add a wrestler to the collection"""
        self.wrestlers.append(wrestler)
    
    def remove_wrestler(self, wrestler_name: str) -> None:
        """Remove a wrestler by name"""
        self.wrestlers = [w for w in self.wrestlers if w.name != wrestler_name]
    
    def get_wrestler(self, wrestler_name: str) -> Optional[Wrestler]:
        """Get a wrestler by name"""
        for w in self.wrestlers:
            if w.name == wrestler_name:
                return w
        return None
    
    def get_wrestlers_by_tv_grade(self, tv_grade: str) -> List[Wrestler]:
        """Get all wrestlers with a specific TV grade"""
        return [w for w in self.wrestlers if w.tv_grade == tv_grade]
    
    def get_top_grudge_wrestlers(self, count: int = 2, excluded_names: List[str] = None) -> List[Wrestler]:
        """Get the top wrestlers by grudge grade, excluding specified wrestlers"""
        excluded = set(excluded_names or [])
        eligible_wrestlers = [w for w in self.wrestlers if w.name not in excluded]
        return sorted(eligible_wrestlers, key=lambda w: abs(w.grudge_grade), reverse=True)[:count]
    
    def get_available_opponents(self, wrestler: Wrestler) -> List[Wrestler]:
        """Get wrestlers that are suitable opponents based on TV grade"""
        # Get wrestlers within one TV grade up or down
        tv_grades = ["AAA", "AA", "A", "B", "C", "D", "E", "F"]
        try:
            wrestler_index = tv_grades.index(wrestler.tv_grade)
            
            min_index = max(0, wrestler_index - 1)
            max_index = min(len(tv_grades) - 1, wrestler_index + 1)
            
            valid_grades = tv_grades[min_index:max_index + 1]
            
            return [w for w in self.wrestlers 
                    if w.tv_grade in valid_grades and w.name != wrestler.name]
        except ValueError:
            # In case the TV grade is not in the standard list
            logger.warning(f"Invalid TV grade: {wrestler.tv_grade}")
            return [w for w in self.wrestlers if w.name != wrestler.name]
    
    def get_allies(self, wrestler: Wrestler) -> List[Wrestler]:
        """Get all wrestlers that are allies of the given wrestler"""
        return [w for w in self.wrestlers if w.name in wrestler.allies]
    
    def get_rivals(self, wrestler: Wrestler) -> List[Wrestler]:
        """Get all wrestlers that are rivals of the given wrestler"""
        return [w for w in self.wrestlers if w.name in wrestler.rivals]
    
    def update_wrestler_grade(self, wrestler_name: str, grade_type: str, new_value: Union[str, int]) -> str:
        """Update a wrestler's TV or Grudge grade"""
        wrestler = self.get_wrestler(wrestler_name)
        if wrestler:
            old_value = wrestler.grudge_grade if grade_type.upper() == "GRUDGE" else wrestler.tv_grade
            
            if grade_type.upper() == "GRUDGE":
                try:
                    wrestler.grudge_grade = int(new_value)
                except ValueError:
                    return f"Invalid grudge grade value: {new_value}. Must be an integer."
            elif grade_type.upper() == "TV":
                if new_value in ["AAA", "AA", "A", "B", "C", "D", "E", "F"]:
                    wrestler.tv_grade = new_value
                else:
                    return f"Invalid TV grade value: {new_value}. Must be one of AAA, AA, A, B, C, D, E, F."
            else:
                return f"Invalid grade type: {grade_type}. Must be TV or GRUDGE."
            
            self.save_wrestlers()
            return f"Updated {wrestler_name}'s {grade_type} grade from {old_value} to {new_value}"
        
        return f"Wrestler {wrestler_name} not found"