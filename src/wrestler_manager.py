import json
import os
from typing import Dict, List, Union, Optional, Tuple, Any

class Wrestler:
    """
    Represents a wrestler in the Face to the Mat game.
    
    Wrestlers have various attributes including TV grade, grudge grade, skills,
    and special moves that determine their capabilities in matches.
    
    Attributes:
        name (str): Wrestler's name
        sex (str): Wrestler's gender
        height (str): Wrestler's height
        weight (str): Wrestler's weight
        hometown (str): Wrestler's hometown
        tv_grade (str): TV popularity grade (AAA, AA, A, B, C, D, E, F)
        grudge_grade (int): Intensity of feuds and rivalries
        skills (Dict[str, str]): Dictionary of skills and their types (STAR, CIRCLE, SQUARE)
        specialty (Dict): Wrestler's specialty move details
        finisher (Dict): Wrestler's finishing move details
        position (int): Current position on the match track (0-15)
        last_card_scored (bool): Whether the wrestler scored on the last card
        is_title_holder (bool): Whether the wrestler holds a title
        allies (List[str]): Names of allied wrestlers
        rivals (List[str]): Names of rival wrestlers
    """
    def __init__(self, name: str, sex: str, height: str, weight: str, hometown: str,
                 tv_grade: str, grudge_grade: Union[int, str], skills: Dict[str, str],
                 specialty: Optional[Dict] = None, finisher: Optional[Dict] = None,
                 image: str = "placeholder.png", allies: Optional[List[str]] = None,
                 rivals: Optional[List[str]] = None, game=None):
        """
        Initialize a wrestler with the given attributes.
        
        Args:
            name: Wrestler's name
            sex: Wrestler's gender
            height: Wrestler's height
            weight: Wrestler's weight
            hometown: Wrestler's hometown
            tv_grade: TV popularity grade
            grudge_grade: Intensity of feuds
            skills: Dictionary of skills and their types
            specialty: Wrestler's specialty move details
            finisher: Wrestler's finishing move details
            image: Filename of wrestler's image
            allies: List of allied wrestler names
            rivals: List of rival wrestler names
            game: Reference to the Game object (optional)
        """
        self.game = game
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
                    self.finisher['range'] = tuple(map(int, self.finisher['range'].split('-')))
                except (ValueError, AttributeError):
                    self.finisher['range'] = (11, 33)  # Default range if parsing fails
        
        self.image = image
        self.position = 0
        self.last_card_scored = False
        self.is_title_holder = False
        
        # Initialize allies and rivals
        self.allies = allies or []
        self.rivals = rivals or []

    def can_use_skill(self, skill: str, position: int) -> bool:
        """
        Determine if the wrestler can use a specific skill at the current position.
        
        Args:
            skill: The skill to check
            position: The wrestler's current position on the match track
            
        Returns:
            bool: True if the wrestler can use the skill, False otherwise
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
        """
        Check if the wrestler has a specific skill.
        
        Args:
            skill: The skill to check for
            
        Returns:
            bool: True if the wrestler has the skill, False otherwise
        """
        return skill.lower() in self.skills

    def has_specialty(self) -> bool:
        """
        Check if the wrestler has a valid specialty move.
        
        Returns:
            bool: True if the wrestler has a specialty, False otherwise
        """
        return bool(self.specialty and self.specialty.get('name') and self.specialty.get('points'))

    def is_trailing(self, opponent) -> bool:
        """
        Check if this wrestler is trailing the opponent on the match track.
        In case of a tie, the underdog is considered trailing.
        
        Args:
            opponent: The opponent wrestler to compare against
            
        Returns:
            bool: True if this wrestler is trailing, False otherwise
        """
        return (self.position < opponent.position or 
                (self.position == opponent.position and self == self.game.underdog_wrestler))

    def score(self, points: int) -> None:
        """
        Add points to the wrestler's position on the match track.
        Position is capped at 15 (FINISHER space).
        
        Args:
            points: Number of points to add
        """
        self.position += points
        self.position = min(self.position, 15)
        self.last_card_scored = True

    @property
    def specialty_points(self) -> int:
        """
        Get the points value of the wrestler's specialty move.
        
        Returns:
            int: The specialty move's point value
        """
        return int(self.specialty.get('points', 0))

    def add_ally(self, ally_name: str) -> None:
        """
        Add a wrestler as an ally.
        
        Args:
            ally_name: Name of the wrestler to add as an ally
        """
        if ally_name not in self.allies and ally_name != self.name:
            self.allies.append(ally_name)

    def add_rival(self, rival_name: str) -> None:
        """
        Add a wrestler as a rival.
        
        Args:
            rival_name: Name of the wrestler to add as a rival
        """
        if rival_name not in self.rivals and rival_name != self.name:
            self.rivals.append(rival_name)

    def remove_ally(self, ally_name: str) -> None:
        """
        Remove a wrestler from allies.
        
        Args:
            ally_name: Name of the wrestler to remove
        """
        if ally_name in self.allies:
            self.allies.remove(ally_name)

    def remove_rival(self, rival_name: str) -> None:
        """
        Remove a wrestler from rivals.
        
        Args:
            rival_name: Name of the wrestler to remove
        """
        if rival_name in self.rivals:
            self.rivals.remove(rival_name)
    
    def to_dict(self) -> Dict:
        """
        Convert the wrestler to a dictionary suitable for JSON serialization.
        
        Returns:
            Dict: Dictionary representation of the wrestler
        """
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
    """
    Manages the collection of wrestlers in the Face to the Mat game.
    
    This class handles loading, saving, and managing wrestlers,
    as well as determining matches, rivalries, and alliances.
    
    Attributes:
        wrestlers (List[Wrestler]): List of all wrestlers
        data_path (str): Path to the wrestler data file
    """
    def __init__(self, data_path: Optional[str] = None, game=None):
        """
        Initialize the WrestlerManager.
        
        Args:
            data_path: Path to the wrestler data file. If None, uses default path.
            game: Reference to the Game object (optional)
        """
        self.game = game
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
        """
        Load wrestlers from the JSON file.
        
        Raises:
            FileNotFoundError: If the wrestler file is not found
            json.JSONDecodeError: If the wrestler file contains invalid JSON
        """
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
            
            self.wrestlers = []
            for w in data['wrestlers']:
                # Handle allies and rivals if they exist in the data
                allies = w.get('allies', [])
                rivals = w.get('rivals', [])
                
                wrestler = Wrestler(game=self.game, allies=allies, rivals=rivals, **w)
                self.wrestlers.append(wrestler)
                
        except FileNotFoundError:
            print(f"Error: wrestlers.json not found at {self.data_path}")
            self.wrestlers = []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in wrestlers.json")
            self.wrestlers = []
    
    def save_wrestlers(self) -> None:
        """
        Save the wrestlers to the JSON file.
        """
        data = {"wrestlers": [w.to_dict() for w in self.wrestlers]}
        
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_wrestler(self, wrestler: Wrestler) -> None:
        """
        Add a wrestler to the collection.
        
        Args:
            wrestler: The wrestler to add
        """
        self.wrestlers.append(wrestler)
    
    def remove_wrestler(self, wrestler_name: str) -> None:
        """
        Remove a wrestler from the collection by name.
        
        Args:
            wrestler_name: Name of the wrestler to remove
        """
        self.wrestlers = [w for w in self.wrestlers if w.name != wrestler_name]
    
    def get_wrestler(self, wrestler_name: str) -> Optional[Wrestler]:
        """
        Get a wrestler by name.
        
        Args:
            wrestler_name: Name of the wrestler to retrieve
            
        Returns:
            Optional[Wrestler]: The wrestler if found, None otherwise
        """
        for w in self.wrestlers:
            if w.name == wrestler_name:
                return w
        return None
    
    def get_wrestlers_by_tv_grade(self, tv_grade: str) -> List[Wrestler]:
        """
        Get wrestlers with a specific TV grade.
        
        Args:
            tv_grade: The TV grade to filter by
            
        Returns:
            List[Wrestler]: List of wrestlers with the specified TV grade
        """
        return [w for w in self.wrestlers if w.tv_grade == tv_grade]
    
    def get_top_grudge_wrestlers(self, count: int = 2) -> List[Wrestler]:
        """
        Get the top wrestlers by grudge grade.
        
        Args:
            count: Number of wrestlers to return
            
        Returns:
            List[Wrestler]: List of top wrestlers by grudge grade
        """
        return sorted(self.wrestlers, key=lambda w: w.grudge_grade, reverse=True)[:count]
    
    def get_available_opponents(self, wrestler: Wrestler) -> List[Wrestler]:
        """
        Get potential opponents for a wrestler based on similar TV grade.
        
        Args:
            wrestler: The wrestler to find opponents for
            
        Returns:
            List[Wrestler]: List of potential opponents
        """
        # Get wrestlers within one TV grade up or down
        tv_grades = ["AAA", "AA", "A", "B", "C", "D", "E", "F"]
        wrestler_index = tv_grades.index(wrestler.tv_grade)
        
        min_index = max(0, wrestler_index - 1)
        max_index = min(len(tv_grades) - 1, wrestler_index + 1)
        
        valid_grades = tv_grades[min_index:max_index + 1]
        
        return [w for w in self.wrestlers 
                if w.tv_grade in valid_grades and w.name != wrestler.name]
    
    def get_allies(self, wrestler: Wrestler) -> List[Wrestler]:
        """
        Get the allies of a wrestler.
        
        Args:
            wrestler: The wrestler to get allies for
            
        Returns:
            List[Wrestler]: List of allied wrestlers
        """
        return [w for w in self.wrestlers if w.name in wrestler.allies]
    
    def get_rivals(self, wrestler: Wrestler) -> List[Wrestler]:
        """
        Get the rivals of a wrestler.
        
        Args:
            wrestler: The wrestler to get rivals for
            
        Returns:
            List[Wrestler]: List of rival wrestlers
        """
        return [w for w in self.wrestlers if w.name in wrestler.rivals]
    
    def update_wrestler_grade(self, wrestler_name: str, grade_type: str, new_value: Union[str, int]) -> str:
        """
        Update a wrestler's TV or Grudge grade.
        
        Args:
            wrestler_name: Name of the wrestler to update
            grade_type: Either "TV" or "GRUDGE"
            new_value: The new grade value
            
        Returns:
            str: Result message
        """
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