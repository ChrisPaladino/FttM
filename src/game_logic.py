from typing import Dict, List, Optional, Union, Tuple, Any
import logging
import os
import json
import random

from wrestler_manager import WrestlerManager, Wrestler
from card_manager import CardManager, Card
from game_utilities import (
    roll_d6, roll_d66, get_pin_range, get_space_type,
    compare_tv_grades, format_log_message, logger
)

class Game:
    def __init__(self):
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

    def play_turn(self) -> str:
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Please select wrestlers to begin the game."
            
        if self.game_over:
            return "The match is over. Start a new match to continue."
        
        initial_control = f"Current in control: {self.in_control.name if self.in_control else 'Neither'}"
        
        # Reset last_card_scored flags for both wrestlers
        if self.favored_wrestler:
            self.favored_wrestler.last_card_scored = False
        if self.underdog_wrestler:
            self.underdog_wrestler.last_card_scored = False
        
        # Draw a card
        self.current_card = self.card_manager.draw_card()
        if not self.current_card:
            return "No cards available. Game cannot continue."
        
        # Log the card information
        card_info = f"Card drawn: {self.current_card.type} ({'Control' if self.current_card.control else 'No Control'})"
        if self.current_card.text:
            card_info += f"\nCard text: {self.current_card.text}"
            
        # Resolve the card
        result = self.resolve_card(self.current_card)
        
        # Log the new in-control wrestler
        new_control = f"New in control: {self.in_control.name if self.in_control else 'Neither'}"
        
        turn_result = f"{initial_control}\n{card_info}\n{result}\n{new_control}\n"
        
        # Check for PIN or FINISHER opportunity
        if self.in_control:  # Only check if someone is in control
            space_type = get_space_type(self.in_control.position)
            
            if space_type == "PIN":
                pin_result = self.attempt_pin()
                turn_result += f"\n{pin_result}"
                
                if "wins by pinfall" in pin_result:
                    self.game_over = True
                    return turn_result
                    
            elif self.in_control.position == 15:  # FINISHER space
                finisher_result = self.attempt_finisher(self.in_control)
                turn_result += f"\n{finisher_result}"
                
                if "They win the match" in finisher_result:
                    self.game_over = True
                    return turn_result
        
        # Check if any wrestler has moved beyond position 15
        for wrestler in [self.favored_wrestler, self.underdog_wrestler]:
            if wrestler and wrestler.position > 15:
                wrestler.position = 15
        
        return turn_result

    def attempt_finisher(self, wrestler: Wrestler) -> str:
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

    def resolve_card(self, card: Card) -> str:
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
        elif card_type == "helped":
            return result + "\n" + self.resolve_helped_card(card)
        elif card_type == "highlight reel":
            return result + "\n" + self.resolve_highlight_reel(card)
        elif card_type == "test of strength":
            return result + "\n" + self.resolve_test_of_strength(card)
        elif card_type == "signature":
            return result + "\n" + self.resolve_signature_card(card)
        elif card_type == "ref bump":
            return result + "\n" + "Ref Bump card drawn. This feature will be implemented in a future update."
        elif card_type == "title holder":
            return result + "\n" + self.resolve_title_holder_card(card)
        else:
            # Skill-specific cards (Agile, Strong, etc.)
            # Check if the card has submission text
            if card.is_submission:
                favored_can_use = self.favored_wrestler.can_use_skill(card_type, self.favored_wrestler.position)
                underdog_can_use = self.underdog_wrestler.can_use_skill(card_type, self.underdog_wrestler.position)
                
                if favored_can_use and underdog_can_use:
                    tie_winner = self.resolve_tiebreaker_without_move(card)
                    return result + "\n" + self.resolve_submission_card(card, tie_winner)
                elif favored_can_use:
                    return result + "\n" + self.resolve_submission_card(card, self.favored_wrestler)
                elif underdog_can_use:
                    return result + "\n" + self.resolve_submission_card(card, self.underdog_wrestler)
                else:
                    return result + "\n" + "Neither wrestler can use this submission. No points scored."
            else:
                return result + "\n" + self.resolve_skill_card(card)

    def resolve_in_control_card(self, card: Card) -> str:
        if not self.in_control:
            return "No wrestler is in control. Cannot resolve in-control card."
            
        result = f"In-control card ({card.type}) for {self.in_control.name}:\n"
        return result + self.move_wrestler(self.in_control, card)

    def resolve_grudge_card(self, card: Card) -> str:
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

    def resolve_helped_card(self, card: Card) -> str:
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve card: wrestlers not set."
        
        # Determine which wrestler has help (from Hot Box)
        favored_has_help = self.favored_ally is not None
        underdog_has_help = self.underdog_ally is not None
        
        if favored_has_help and underdog_has_help:
            # Both have help, use tiebreaker
            result = "Both wrestlers have help. Using tiebreaker.\n"
            winner = self.resolve_tiebreaker_without_move(card)
            ally = self.favored_ally if winner == self.favored_wrestler else self.underdog_ally
            
            result += self._helped_card_logic(card, winner, ally)
            self.in_control = winner
            return result
        elif favored_has_help:
            result = self._helped_card_logic(card, self.favored_wrestler, self.favored_ally)
            self.in_control = self.favored_wrestler
            return result
        elif underdog_has_help:
            result = self._helped_card_logic(card, self.underdog_wrestler, self.underdog_ally)
            self.in_control = self.underdog_wrestler
            return result
        else:
            return "Neither wrestler has outside help. No points scored."

    def _helped_card_logic(self, card: Card, wrestler: Wrestler, ally: Optional[Wrestler] = None) -> str:
        """Internal helper function to implement Helped card logic"""
        result = f"{wrestler.name} receives outside help"
        
        if ally:
            result += f" from {ally.name}"
        
        # If the card has points, apply them
        if isinstance(card.points, (int, float, str)) or (isinstance(card.points, dict) and wrestler.tv_grade in card.points):
            points = card.get_points(wrestler.tv_grade)
            wrestler.score(points)
            result += f". They score {points} points and move to position {wrestler.position}."
            wrestler.last_card_scored = True
        # If the card has text but no points, it's a special effect
        elif card.text:
            # Handle Highlight Reel reference
            if "HIGHLIGHT REEL" in card.text:
                result += ".\n" + card.text
                # Log that this needs future implementation
                result += "\n(Highlight Reel functionality will be implemented in a future update.)"
        else:
            result += ", but it had no effect."
        
        return result

    def resolve_highlight_reel(self, card: Card) -> str:
        # This is a stub to be expanded with actual highlight reel mechanics
        if card.text:
            result = f"Highlight Reel card: {card.text}\n"
            result += "Highlight Reel functionality will be implemented in a future update."
            return result
        else:
            return "Highlight Reel card drawn, but no text specified."

    def resolve_skill_card(self, card: Card) -> str:
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
        if not wrestler:
            return "Cannot resolve submission: wrestler not specified."
            
        opponent = self.underdog_wrestler if wrestler == self.favored_wrestler else self.favored_wrestler
        if not opponent:
            return "Cannot resolve submission: opponent not found."
        
        result = f"{wrestler.name} attempts a submission move!\n"
        
        # Initial points
        points_scored = card.get_points(wrestler.tv_grade)
        wrestler.score(points_scored)
        result += f"{wrestler.name} scores {points_scored} point(s). Position: {wrestler.position}\n"
        
        # Determine break threshold based on opponent's strength
        opponent_is_strong = opponent.has_skill('strong') or opponent.has_skill('powerful')
        break_threshold = 4 if opponent_is_strong else 3
        
        # Continue until opponent breaks free
        while True:
            roll = roll_d6()
            result += f"{opponent.name} attempts to break free (roll: {roll}, needs {break_threshold} or less).\n"
            
            if roll <= break_threshold:
                result += f"{opponent.name} breaks the hold.\n"
                break
            else:
                wrestler.score(1)
                result += f"{wrestler.name} maintains the hold and scores an additional point. Position: {wrestler.position}\n"
        
        # Set the wrestler who scored as being in control
        wrestler.last_card_scored = True
        self.in_control = wrestler
        
        return result

    def resolve_signature_card(self, card: Card) -> str:
        if self.in_control and self.in_control.last_card_scored:
            roll = roll_d6()
            self.in_control.score(roll)
            return f"{self.in_control.name} used a Signature move and moved to position {self.in_control.position} (d6 roll: {roll})"
        else:
            return "No wrestler eligible for Signature move. No points scored."

    def resolve_test_of_strength(self, card: Card) -> str:
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
                self.in_control = face_wrestler
            elif roll <= 4:
                result += "Referee breaks up the Test of Strength. No points scored.\n"
                break
            else:  # 5-6
                heel_wrestler.score(1)
                result += f"{heel_wrestler.name} wins the exchange and scores 1 point. Position: {heel_wrestler.position}\n"
                self.in_control = heel_wrestler
            
            # Check if ref breaks after scoring
            break_roll = roll_d6()
            if break_roll <= 4:
                result += f"Referee breaks up the Test of Strength (roll: {break_roll}).\n"
                break
        
        return result

    def resolve_tiebreaker(self, card: Card) -> str:
        if not self.favored_wrestler or not self.underdog_wrestler:
            return "Cannot resolve tiebreaker: wrestlers not set."
            
        # First tiebreaker: trailing wrestler gets the move
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.move_wrestler(self.underdog_wrestler, card)
        
        # Second tiebreaker: favored wrestler wins ties
        return self.move_wrestler(self.favored_wrestler, card)

    def resolve_tiebreaker_without_move(self, card: Card) -> Wrestler:
        if not self.favored_wrestler or not self.underdog_wrestler:
            return None
            
        # First tiebreaker: trailing wrestler gets the move
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.favored_wrestler
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.underdog_wrestler
        
        # Second tiebreaker: favored wrestler wins ties
        return self.favored_wrestler

    def resolve_title_holder_card(self, card: Card) -> str:
        if not self.in_control:
            return "No wrestler is in control. Cannot resolve Title Holder card."
            
        if not self.in_control.is_title_holder:
            return f"{self.in_control.name} is not a title holder. No points scored."
        
        # Only title holders can use this card
        return self.move_wrestler(self.in_control, card)

    def resolve_trailing_card(self, card: Card) -> str:
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
        # This is a stub to be expanded with actual wild card mechanics
        if card.text:
            result = f"Wild Card: {card.text}\n"
            result += "Wild Card functionality will be implemented in a future update."
            return result
        else:
            return "Wild Card drawn, but no text specified."

    def move_wrestler(self, wrestler: Wrestler, card: Card) -> str:
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

    def post_match_roll(self, winner: str) -> str:
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
        d6_roll = roll_d6()
        d66_roll = roll_d66()
        
        if 1 <= d6_roll <= 4:
            return f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'O'"
        else:
            return f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'R'"

    def set_wrestler_position(self, wrestler: Wrestler, position: int) -> None:
        if wrestler:
            wrestler.position = min(max(0, position), 15)  # Ensure position is between 0 and 15

    def set_in_control(self, wrestler: Optional[Wrestler]) -> None:
        self.in_control = wrestler

    def setup_game(self) -> None:
        # Load/refresh wrestlers
        self.wrestler_manager.load_wrestlers()
        self.wrestlers = self.wrestler_manager.wrestlers
        
        # Refresh the card deck
        self.card_manager.reset()
        
        # Reset game state
        self.in_control = None
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