from typing import Dict, List, Optional, Union, Tuple, Any
import logging
import os
import json

from wrestler_manager import WrestlerManager, Wrestler
from card_manager import CardManager, Card
from game_utilities import (
    roll_d6, roll_d66, get_pin_range, get_space_type,
    compare_tv_grades, format_log_message, logger
)

class Game:
    """
    The main game class for Face to the Mat.
    
    This class orchestrates the match, handling the game state, card draws,
    wrestler interactions, and scoring.
    
    Attributes:
        in_control_counter (int): Counter for tracking consecutive in-control turns
        in_control (Optional[Wrestler]): Currently in-control wrestler, if any
        favored_wrestler (Optional[Wrestler]): The favored (expected to win) wrestler
        underdog_wrestler (Optional[Wrestler]): The underdog wrestler
        wrestlers (List[Wrestler]): List of all available wrestlers
        deck (List[Card]): Current deck of cards
        discard_pile (List[Card]): Cards that have been played
        current_card (Optional[Card]): The currently drawn card
        game_over (bool): Whether the match has ended
    """
    def __init__(self):
        """Initialize a new game."""
        self.in_control_counter = 0
        self.in_control = None
        self.favored_wrestler = None
        self.underdog_wrestler = None
        
        # Initialize managers
        self.wrestler_manager = WrestlerManager(game=self)
        self.card_manager = CardManager()
        
        # Set up game state
        self.wrestlers = self.wrestler_manager.wrestlers
        self.current_card = None
        self.game_over = False
        
        # Hot box
        self.favored_ally = None
        self.favored_foe = None
        self.underdog_ally = None
        self.underdog_foe = None
        self.grudge_wrestlers = []
        
        logger.info("Game initialized")

    def attempt_finisher(self, wrestler: Wrestler) -> str:
        """
        Attempt a finishing move with the given wrestler.
        
        Args:
            wrestler: The wrestler attempting the finisher
            
        Returns:
            str: A description of the attempt result
        """
        if not wrestler.finisher:
            return f"{wrestler.name} doesn't have a finisher move defined."
        
        result = f"{wrestler.name} attempts their finisher move: {wrestler.finisher['name']}!\n"
        roll = roll_d66()
        result += f"Dice roll: {roll}\n"
        
        if "range" in wrestler.finisher and roll in range(wrestler.finisher['range'][0], wrestler.finisher['range'][1] + 1):
            result += f"{wrestler.name}'s finisher is successful! They win the match!\n"
            self.game_over = True
        else:
            result += f"{wrestler.name}'s finisher failed. They move back to position 9.\n"
            wrestler.position = 9
        
        return result

    def attempt_pin(self) -> str:
        """
        Attempt a pin with the wrestler who is furthest along the board.
        
        Returns:
            str: A description of the pin attempt result
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot attempt pin: wrestlers not set."
            
        pinner = max([self.favored_wrestler, self.underdog_wrestler], key=lambda w: w.position)
        defender = self.underdog_wrestler if pinner == self.favored_wrestler else self.favored_wrestler
        
        kick_out_range = get_pin_range(defender.tv_grade)
        result = f"{pinner.name} attempts a pin on {defender.name}!\n"
        result += f"{defender.name}'s kick out range (TV Grade {defender.tv_grade}): {kick_out_range.start}-{kick_out_range.stop - 1}\n"
        
        for count in range(1, 4):
            roll = roll_d66()
            result += f"Count {count}: {defender.name} rolled {roll}\n"
            
            if roll in kick_out_range:
                result += f"{defender.name} kicks out at {count}!\n"
                return result
        
        result += f"{defender.name} fails to kick out. {pinner.name} wins by pinfall!\n"
        self.game_over = True
        return result

    def play_turn(self) -> str:
        """
        Play a turn in the match by drawing a card and resolving its effects.
        
        Returns:
            str: A description of the turn's events
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Please select wrestlers to begin the game."
            
        if self.game_over:
            return "The match is over. Start a new match to continue."
        
        initial_control = f"Current in control: {self.in_control.name if self.in_control else 'Neither'}"
        
        self.current_card = self.card_manager.draw_card()
        if not self.current_card:
            return "No cards available. Game cannot continue."
        
        card_info = f"Card drawn: {self.current_card.type} ({'Control' if self.current_card.control else 'No Control'})"
        if self.current_card.text:
            card_info += f"\nCard text: {self.current_card.text}"
            
        result = self.resolve_card(self.current_card)
        
        new_control = f"New in control: {self.in_control.name if self.in_control else 'Neither'}"
        
        turn_result = f"{initial_control}\n{card_info}\n{result}\n{new_control}\n"
        
        # Check for PIN or FINISHER opportunity only for the wrestler who just moved
        active_wrestler = self.in_control  # Assuming the wrestler who just scored is now in control
        if active_wrestler:
            space_type = get_space_type(active_wrestler.position)
            
            if space_type == "PIN":
                pin_result = self.attempt_pin()
                turn_result += f"\n{pin_result}"
                
                if "wins by pinfall" in pin_result:
                    self.game_over = True
                    return turn_result
                    
            elif active_wrestler.position == 15:  # FINISHER space
                finisher_result = self.attempt_finisher(active_wrestler)
                turn_result += f"\n{finisher_result}"
                
                if "They win the match" in finisher_result:
                    self.game_over = True
                    return turn_result
        
        # Check if any wrestler has moved beyond position 15
        for wrestler in [self.favored_wrestler, self.underdog_wrestler]:
            if wrestler and wrestler.position > 15:
                wrestler.position = 15
        
        return turn_result

    def post_match_roll(self, winner: str) -> str:
        """
        Perform a post-match roll to determine storyline event.
        
        Args:
            winner: "Face" or "Heel" indicating who won the match
            
        Returns:
            str: Description of the post-match event
        """
        d6_roll = roll_d6()
        d66_roll = roll_d66()
        
        if 1 <= d6_roll <= 4:
            return f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'X'"
        else:
            if winner == "Face":
                return f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Face won. Use Highlight Reel 'T'"
            else:
                return f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Heel won. Use Highlight Reel 'U'"

    def pre_match_roll(self) -> str:
        """
        Perform a pre-match roll to determine storyline event.
        
        Returns:
            str: Description of the pre-match event
        """
        d6_roll = roll_d6()
        d66_roll = roll_d66()
        
        if 1 <= d6_roll <= 4:
            return f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'O'"
        else:
            return f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'R'"

    def resolve_card(self, card: Card) -> str:
        """
        Determine the outcome of a drawn card.
        
        Args:
            card: The card to resolve
            
        Returns:
            str: Description of the card's resolution
        """
        result = f"Card drawn: {card.type} ({'Control' if card.control else 'No Control'})"
        
        # Handle in-control cards first
        if card.control and self.in_control:
            return result + "\n" + self.resolve_in_control_card(card)
        
        # Handle different card types
        card_type = card.type.lower()
        
        if card_type == "tv":
            return result + "\n" + self.resolve_tv_card(card)
        elif card_type == "grudge":
            return result + "\n" + self.resolve_grudge_card(card)
        elif card_type == "specialty":
            return result + "\n" + self.resolve_specialty_card(card)
        elif card_type == "trailing":
            return result + "\n" + self.resolve_trailing_card(card)
        elif card_type == "wild card":
            return result + "\n" + self.resolve_wild_card(card)
        elif card_type == "highlight reel":
            return result + "\n" + self.resolve_highlight_reel(card)
        elif card_type == "test of strength":
            return result + "\n" + self.resolve_test_of_strength(card)
        elif card_type == "signature":
            return result + "\n" + self.resolve_signature_card(card)
        elif card_type == "ref bump":
            return result + "\n" + "Ref Bump card drawn. This feature will be implemented in a future update."
        else:
            # Skill-specific cards (Agile, Strong, etc.)
            return result + "\n" + self.resolve_skill_card(card)

    def resolve_grudge_card(self, card: Card) -> str:
        """
        Resolve a Grudge card by comparing wrestlers' grudge grades.
        
        Args:
            card: The Grudge card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
            
        favored_grudge = self.favored_wrestler.grudge_grade
        underdog_grudge = self.underdog_wrestler.grudge_grade
        
        result = f"Comparing Grudge Grades: {self.favored_wrestler.name} ({favored_grudge}) vs {self.underdog_wrestler.name} ({underdog_grudge})\n"
        
        if favored_grudge > underdog_grudge:
            result += self.move_wrestler(self.favored_wrestler, card)
        elif underdog_grudge > favored_grudge:
            result += self.move_wrestler(self.underdog_wrestler, card)
        else:
            result += "Grudge Grades are equal. Using tiebreaker.\n"
            result += self.resolve_tiebreaker(card)
        
        return result

    def resolve_highlight_reel(self, card: Card) -> str:
        """
        Resolve a Highlight Reel card that references special events.
        
        Args:
            card: The Highlight Reel card to resolve
            
        Returns:
            str: Description of the resolution
        """
        # This is a stub to be expanded with actual highlight reel mechanics
        if card.text:
            result = f"Highlight Reel card: {card.text}\n"
            result += "Highlight Reel functionality will be implemented in a future update."
            return result
        else:
            return "Highlight Reel card drawn, but no text specified."

    def resolve_in_control_card(self, card: Card) -> str:
        """
        Resolve a card when a wrestler is in control.
        
        Args:
            card: The card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if not self.in_control:
            return "No wrestler is in control. Cannot resolve in-control card."
            
        result = f"In-control card ({card.type}) for {self.in_control.name}:\n"
        return result + self.move_wrestler(self.in_control, card)
    
    def resolve_signature_card(self, card: Card) -> str:
        """
        Resolve a Signature card, which allows a wrestler to use a signature move.
        
        Args:
            card: The Signature card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if self.in_control and self.in_control.last_card_scored:
            roll = roll_d6()
            self.in_control.score(roll)
            return f"{self.in_control.name} used a Signature move and moved to position {self.in_control.position} (d6 roll: {roll})"
        else:
            return "No wrestler eligible for Signature move. No points scored."

    def resolve_skill_card(self, card: Card) -> str:
        """
        Resolve a skill-specific card (Agile, Strong, etc.).
        
        Args:
            card: The skill card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
            
        favored_can_use = self.favored_wrestler.can_use_skill(card.type, self.favored_wrestler.position)
        underdog_can_use = self.underdog_wrestler.can_use_skill(card.type, self.underdog_wrestler.position)

        result = f"Checking if wrestlers can use {card.type}:\n"
        result += f"{self.favored_wrestler.name} can use: {favored_can_use}\n"
        result += f"{self.underdog_wrestler.name} can use: {underdog_can_use}\n"

        if favored_can_use and underdog_can_use:
            result += "Both wrestlers can use this skill. Using tiebreaker.\n"
            result += self.resolve_tiebreaker(card)
        elif favored_can_use:
            result += self.move_wrestler(self.favored_wrestler, card)
        elif underdog_can_use:
            result += self.move_wrestler(self.underdog_wrestler, card)
        else:
            result += "Neither wrestler can use this skill. No points scored."

        return result

    def resolve_specialty_card(self, card: Card, in_control_wrestler: Optional[Wrestler] = None) -> str:
        """
        Resolve a Specialty card, which allows wrestlers to use their specialty moves.
        
        Args:
            card: The Specialty card to resolve
            in_control_wrestler: The wrestler in control (if any)
            
        Returns:
            str: Description of the resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
            
        result = "Specialty card drawn. "
        
        if in_control_wrestler:
            if in_control_wrestler.has_specialty():
                return result + self.move_wrestler(in_control_wrestler, card)
            else:
                other_wrestler = self.underdog_wrestler if in_control_wrestler == self.favored_wrestler else self.favored_wrestler
                if other_wrestler.has_specialty():
                    return result + self.move_wrestler(other_wrestler, card)
                else:
                    return result + "Neither wrestler has a Specialty defined. No points scored."
        
        if self.favored_wrestler.has_specialty() and self.underdog_wrestler.has_specialty():
            result += "Both wrestlers have specialties. Using tiebreaker.\n"
            return result + self.resolve_tiebreaker(card)
        elif self.favored_wrestler.has_specialty():
            return result + self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.has_specialty():
            return result + self.move_wrestler(self.underdog_wrestler, card)
        else:
            return result + "Neither wrestler has a Specialty defined. No points scored."

    def resolve_submission_card(self, card: Card, wrestler: Wrestler) -> str:
        """
        Resolve a Submission card, which allows a wrestler to apply a submission hold.
        
        Args:
            card: The Submission card to resolve
            wrestler: The wrestler applying the submission
            
        Returns:
            str: Description of the resolution
        """
        if not wrestler:
            return "Cannot resolve submission: wrestler not specified."
            
        opponent = self.underdog_wrestler if wrestler == self.favored_wrestler else self.favored_wrestler
        if not opponent:
            return "Cannot resolve submission: opponent not found."
            
        result = f"{wrestler.name} attempts a submission move!\n"
        points_scored = card.get_points(wrestler.tv_grade)
        wrestler.score(points_scored)
        result += f"{wrestler.name} scores {points_scored} point(s). Position: {wrestler.position}\n"
        
        opponent_is_strong = opponent.has_skill('strong') or opponent.has_skill('powerful')
        
        while True:
            roll = roll_d6()
            break_hold = 3 if not opponent_is_strong else 4
            if roll <= break_hold:
                result += f"{opponent.name} breaks the hold with a roll of {roll}.\n"
                break
            else:
                wrestler.score(1)
                result += f"{wrestler.name} scores an additional point. Position: {wrestler.position}\n"
        
        return result

    def resolve_test_of_strength(self, card: Card) -> str:
        """
        Resolve a Test of Strength card, which is a special contest between wrestlers.
        
        Args:
            card: The Test of Strength card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
            
        # Determine which wrestler is face (good guy) and heel (bad guy)
        # For simplicity, we'll assume favored is face and underdog is heel
        face_wrestler = self.favored_wrestler
        heel_wrestler = self.underdog_wrestler
        
        # Check if both wrestlers are strong/powerful
        face_qualified = face_wrestler.has_skill('strong') or face_wrestler.has_skill('powerful')
        heel_qualified = heel_wrestler.has_skill('strong') or heel_wrestler.has_skill('powerful')
        
        result = "Test of Strength card drawn.\n"
        result += f"{face_wrestler.name} can participate: {face_qualified}\n"
        result += f"{heel_wrestler.name} can participate: {heel_qualified}\n"
        
        if not (face_qualified and heel_qualified):
            return result + "Both wrestlers must have STRONG or POWERFUL skills. No points scored."
        
        result += "Both wrestlers qualify for Test of Strength.\n"
        
        # Roll until ref breaks
        while True:
            roll = roll_d6()
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
            break_roll = roll_d6()
            if break_roll <= 4:
                result += f"Referee breaks up the Test of Strength (roll: {break_roll}).\n"
                break
        
        return result

    def resolve_tiebreaker(self, card: Card) -> str:
        """
        Resolve a tiebreaker when both wrestlers can perform a move.
        
        Args:
            card: The card being resolved
            
        Returns:
            str: Description of the tiebreaker resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve tiebreaker: wrestlers not set."
            
        # First tiebreaker: trailing wrestler gets the move
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.move_wrestler(self.underdog_wrestler, card)
        
        # Second tiebreaker: favored wrestler wins ties
        return self.move_wrestler(self.favored_wrestler, card)

    def resolve_trailing_card(self, card: Card) -> str:
        """
        Resolve a Trailing card, which benefits the wrestler who is behind.
        
        Args:
            card: The Trailing card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
            
        if self.favored_wrestler.is_trailing(self.underdog_wrestler):
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.is_trailing(self.favored_wrestler):
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            # If positions are equal, the underdog is considered trailing
            if self.favored_wrestler.position == self.underdog_wrestler.position:
                return self.move_wrestler(self.underdog_wrestler, card)
            else:
                return "Neither wrestler is trailing. No points scored."

    def resolve_tv_card(self, card: Card) -> str:
        """
        Resolve a TV card by comparing wrestlers' TV grades.
        
        Args:
            card: The TV card to resolve
            
        Returns:
            str: Description of the resolution
        """
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
            
        favored_grade = self.favored_wrestler.tv_grade
        underdog_grade = self.underdog_wrestler.tv_grade
        
        result = f"Comparing TV Grades: {self.favored_wrestler.name} ({favored_grade}) vs {self.underdog_wrestler.name} ({underdog_grade})\n"
        
        comparison = compare_tv_grades(favored_grade, underdog_grade)
        
        if comparison > 0:  # favored has better grade
            result += self.move_wrestler(self.favored_wrestler, card)
        elif comparison < 0:  # underdog has better grade
            result += self.move_wrestler(self.underdog_wrestler, card)
        else:  # equal grades
            result += "TV Grades are equal. Using tiebreaker.\n"
            result += self.resolve_tiebreaker(card)
        
        return result

    def resolve_wild_card(self, card: Card) -> str:
        """
        Resolve a Wild Card, which triggers a special event.
        
        Args:
            card: The Wild Card to resolve
            
        Returns:
            str: Description of the resolution
        """
        # This is a stub to be expanded with actual wild card mechanics
        if card.text:
            result = f"Wild Card: {card.text}\n"
            result += "Wild Card functionality will be implemented in a future update."
            return result
        else:
            return "Wild Card drawn, but no text specified."

    def move_wrestler(self, wrestler: Wrestler, card: Card) -> str:
        """
        Move a wrestler based on the points from a card.
        
        Args:
            wrestler: The wrestler to move
            card: The card providing the points
            
        Returns:
            str: Description of the move
        """
        if not wrestler:
            return "Cannot move: wrestler not specified."
            
        if card.type.lower() == "tv":
            points = card.get_points(wrestler.tv_grade)
        elif card.type.lower() == "specialty":
            points = wrestler.specialty_points
        elif card.type.lower() == "signature":
            points = roll_d6()
        else:
            points = card.get_points(wrestler.tv_grade)
        
        original_position = wrestler.position
        wrestler.score(points)
        
        result = f"{wrestler.name} used {card.type} "
        if card.type.lower() == "specialty" and wrestler.specialty:
            result += f"({wrestler.specialty.get('name', 'Unnamed Specialty')}) "
        
        result += f"and moved from position {original_position} to {wrestler.position} (+{points} points)"

        if points > 0:
            self.in_control = wrestler
            result += f"\n{wrestler.name} is now in control."
        
        return result

    def set_wrestler_position(self, wrestler: Wrestler, position: int) -> None:
        """
        Set a wrestler's position on the match track.
        
        Args:
            wrestler: The wrestler to move
            position: The position to move to
        """
        if wrestler:
            wrestler.position = min(max(0, position), 15)  # Ensure position is between 0 and 15

    def set_in_control(self, wrestler: Optional[Wrestler]) -> None:
        """
        Set which wrestler is in control.
        
        Args:
            wrestler: The wrestler to set as in control, or None for neither
        """
        self.in_control = wrestler

    def setup_game(self) -> None:
        """Set up the game by loading/initializing resources."""
        # Load/refresh wrestlers
        self.wrestler_manager.load_wrestlers()
        self.wrestlers = self.wrestler_manager.wrestlers
        
        # Refresh the card deck
        self.card_manager.reset()
        
        # Reset game state
        self.in_control = None
        self.in_control_counter = 0
        self.favored_wrestler = None
        self.underdog_wrestler = None
        self.current_card = None
        self.game_over = False
        
        # Reset hot box
        self.favored_ally = None
        self.favored_foe = None
        self.underdog_ally = None
        self.underdog_foe = None
        self.grudge_wrestlers = []
        
        logger.info("Game setup complete")

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
        return self.wrestler_manager.update_wrestler_grade(wrestler_name, grade_type, new_value)

    def get_top_grudge_wrestlers(self, count: int = 2, exclude: Optional[List[str]] = None) -> List[Wrestler]:
        """
        Get the top wrestlers by grudge grade, excluding specified wrestlers.
        
        Args:
            count: Number of wrestlers to return
            exclude: Names of wrestlers to exclude
            
        Returns:
            List[Wrestler]: List of top wrestlers by grudge grade
        """
        exclude = exclude or []
        wrestlers = [w for w in self.wrestlers if w.name not in exclude]
        return sorted(wrestlers, key=lambda w: w.grudge_grade, reverse=True)[:count]

    def setup_hot_box(self, 
                     favored_ally_name: Optional[str] = None,
                     favored_foe_name: Optional[str] = None,
                     underdog_ally_name: Optional[str] = None,
                     underdog_foe_name: Optional[str] = None) -> None:
        """
        Set up the Hot Box with allies and foes.
        
        Args:
            favored_ally_name: Name of the favored wrestler's ally
            favored_foe_name: Name of the favored wrestler's foe
            underdog_ally_name: Name of the underdog wrestler's ally
            underdog_foe_name: Name of the underdog wrestler's foe
        """
        # Clear existing hot box
        self.favored_ally = None
        self.favored_foe = None
        self.underdog_ally = None
        self.underdog_foe = None
        
        # Set new hot box members
        if favored_ally_name:
            self.favored_ally = self.wrestler_manager.get_wrestler(favored_ally_name)
        
        if favored_foe_name:
            self.favored_foe = self.wrestler_manager.get_wrestler(favored_foe_name)
        
        if underdog_ally_name:
            self.underdog_ally = self.wrestler_manager.get_wrestler(underdog_ally_name)
        
        if underdog_foe_name:
            self.underdog_foe = self.wrestler_manager.get_wrestler(underdog_foe_name)
        
        # Set top grudge wrestlers
        excluded_names = [
            n for n in [
                self.favored_wrestler.name if self.favored_wrestler else None,
                self.underdog_wrestler.name if self.underdog_wrestler else None,
                favored_ally_name, favored_foe_name, underdog_ally_name, underdog_foe_name
            ] if n is not None
        ]
        
        self.grudge_wrestlers = self.get_top_grudge_wrestlers(2, exclude=excluded_names)