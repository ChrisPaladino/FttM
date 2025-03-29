"""
Face to the Mat - Core Game Logic
This module contains the core game mechanics separated from UI concerns.
"""
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
import logging
import os
import json
import random
from enum import Enum, auto

from wrestler_manager import WrestlerManager, Wrestler
from card_manager import CardManager, Card
from game_utilities import (
    roll_d6, roll_d66, get_pin_range, get_space_type,
    compare_tv_grades, format_log_message, logger
)

class GameEvent(Enum):
    """Events that can be triggered during gameplay"""
    CARD_DRAWN = auto()
    CARD_RESOLVED = auto()
    WRESTLER_MOVED = auto()
    PIN_ATTEMPTED = auto()
    FINISHER_ATTEMPTED = auto()
    MATCH_ENDED = auto()
    IN_CONTROL_CHANGED = auto()
    HOT_BOX_UPDATED = auto()
    ERROR_OCCURRED = auto()

class GameResult:
    """Represents the result of a game action"""
    def __init__(self, success: bool, message: str, data: Dict = None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    def __str__(self) -> str:
        return self.message

class Game:
    """Core game engine for Face to the Mat"""
    
    def __init__(self):
        # Game state
        self.in_control = None
        self.favored_wrestler = None
        self.underdog_wrestler = None
        self.current_card = None
        self.game_over = False
        
        # Initialize managers
        self.wrestler_manager = WrestlerManager()
        self.card_manager = CardManager()
        self.wrestlers = self.wrestler_manager.wrestlers
        
        # Hot box
        self.favored_ally = None
        self.favored_foe = None
        self.underdog_ally = None
        self.underdog_foe = None
        self.grudge_wrestlers = []
        
        # Event listeners
        self._event_listeners = {event: [] for event in GameEvent}
        
        logger.info("Game engine initialized")

    def add_event_listener(self, event: GameEvent, callback: Callable):
        """Register a callback for a specific game event"""
        if event in self._event_listeners:
            self._event_listeners[event].append(callback)
    
    def remove_event_listener(self, event: GameEvent, callback: Callable):
        """Remove a callback for a specific game event"""
        if event in self._event_listeners and callback in self._event_listeners[event]:
            self._event_listeners[event].remove(callback)
    
    def _trigger_event(self, event: GameEvent, data: Dict = None):
        """Trigger an event and notify all listeners"""
        if event in self._event_listeners:
            for callback in self._event_listeners[event]:
                callback(data or {})

    def setup_game(self) -> GameResult:
        """Initialize or reset the game state"""
        try:
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
            return GameResult(True, "Game setup complete")
        except Exception as e:
            logger.error(f"Error during game setup: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error during game setup: {e}")

    def setup_wrestlers(self, favored_name: str, underdog_name: str) -> GameResult:
        """Set up the wrestlers for the match"""
        try:
            # Get wrestler objects
            favored = self.wrestler_manager.get_wrestler(favored_name)
            underdog = self.wrestler_manager.get_wrestler(underdog_name)
            
            if not favored:
                return GameResult(False, f"Favored wrestler '{favored_name}' not found")
            if not underdog:
                return GameResult(False, f"Underdog wrestler '{underdog_name}' not found")
            
            # Reset positions
            favored.position = 0
            underdog.position = 0
            
            # Set wrestlers
            self.favored_wrestler = favored
            self.underdog_wrestler = underdog
            
            # Reset in-control
            self.in_control = None
            
            logger.info(f"Match set up with {favored_name} (Favored) vs {underdog_name} (Underdog)")
            return GameResult(True, f"Match set up: {favored_name} vs {underdog_name}")
        except Exception as e:
            logger.error(f"Error setting up wrestlers: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error setting up wrestlers: {e}")

    def setup_hot_box(self, favored_ally_name: Optional[str] = None, 
                      favored_foe_name: Optional[str] = None,
                      underdog_ally_name: Optional[str] = None, 
                      underdog_foe_name: Optional[str] = None,
                      grudge_wrestler_names: Optional[List[str]] = None) -> GameResult:
        """Set up the Hot Box with allies, foes, and grudge wrestlers"""
        try:
            # Reset Hot Box
            self.favored_ally = None
            self.favored_foe = None
            self.underdog_ally = None
            self.underdog_foe = None
            self.grudge_wrestlers = []
            
            # Set allies and foes if provided
            if favored_ally_name:
                self.favored_ally = self.wrestler_manager.get_wrestler(favored_ally_name)
            if favored_foe_name:
                self.favored_foe = self.wrestler_manager.get_wrestler(favored_foe_name)
            if underdog_ally_name:
                self.underdog_ally = self.wrestler_manager.get_wrestler(underdog_ally_name)
            if underdog_foe_name:
                self.underdog_foe = self.wrestler_manager.get_wrestler(underdog_foe_name)
            
            # Set grudge wrestlers if provided
            if grudge_wrestler_names:
                for name in grudge_wrestler_names:
                    wrestler = self.wrestler_manager.get_wrestler(name)
                    if wrestler:
                        self.grudge_wrestlers.append(wrestler)
            
            # If no grudge wrestlers provided, use the top by grudge grade
            if not self.grudge_wrestlers:
                # Exclude wrestlers already in the match or hot box
                excluded_wrestlers = {
                    self.favored_wrestler.name if self.favored_wrestler else "",
                    self.underdog_wrestler.name if self.underdog_wrestler else "",
                    favored_ally_name or "",
                    favored_foe_name or "",
                    underdog_ally_name or "",
                    underdog_foe_name or ""
                }
                excluded_wrestlers = {name for name in excluded_wrestlers if name}  # Remove empty strings
                
                top_grudge = self.get_top_grudge_wrestlers(2, list(excluded_wrestlers))
                self.grudge_wrestlers = top_grudge
            
            # Trigger event
            self._trigger_event(GameEvent.HOT_BOX_UPDATED, {
                "favored_ally": self.favored_ally.name if self.favored_ally else None,
                "favored_foe": self.favored_foe.name if self.favored_foe else None,
                "underdog_ally": self.underdog_ally.name if self.underdog_ally else None,
                "underdog_foe": self.underdog_foe.name if self.underdog_foe else None,
                "grudge_wrestlers": [w.name for w in self.grudge_wrestlers]
            })
            
            return GameResult(True, "Hot Box updated successfully")
        except Exception as e:
            logger.error(f"Error setting up Hot Box: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error setting up Hot Box: {e}")

    def get_top_grudge_wrestlers(self, count: int = 2, excluded_names: List[str] = None) -> List[Wrestler]:
        """Get the top wrestlers by grudge grade, excluding specified wrestlers"""
        try:
            excluded = set(excluded_names or [])
            eligible_wrestlers = [w for w in self.wrestlers if w.name not in excluded]
            return sorted(eligible_wrestlers, key=lambda w: abs(w.grudge_grade), reverse=True)[:count]
        except Exception as e:
            logger.error(f"Error getting top grudge wrestlers: {e}")
            return []
        
    def play_turn(self) -> GameResult:
        """Execute a single turn of the game"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Please select wrestlers to begin the game.")
            
        if self.game_over:
            return GameResult(False, "The match is over. Start a new match to continue.")
        
        try:
            # Store the current in-control wrestler for comparison later
            previous_control = self.in_control
            
            # Reset last_card_scored flags for both wrestlers
            if self.favored_wrestler:
                self.favored_wrestler.last_card_scored = False
            if self.underdog_wrestler:
                self.underdog_wrestler.last_card_scored = False
            
            # Draw a card
            self.current_card = self.card_manager.draw_card()
            if not self.current_card:
                return GameResult(False, "No cards available. Game cannot continue.")
            
            # Trigger card drawn event
            self._trigger_event(GameEvent.CARD_DRAWN, {
                "card_type": self.current_card.type,
                "control": self.current_card.control,
                "points": self.current_card.points,
                "text": self.current_card.text
            })
            
            # Create card info for logging
            card_info = f"Card drawn: {self.current_card.type} ({'Control' if self.current_card.control else 'No Control'})"
            if self.current_card.text:
                card_info += f"\nCard text: {self.current_card.text}"
                
            # Resolve the card
            resolution_result = self._resolve_card(self.current_card)
            
            # Check if in-control changed
            if previous_control != self.in_control:
                self._trigger_event(GameEvent.IN_CONTROL_CHANGED, {
                    "previous": previous_control.name if previous_control else "None",
                    "current": self.in_control.name if self.in_control else "None"
                })
            
            # Construct the complete turn result
            initial_control = f"Current in control: {previous_control.name if previous_control else 'Neither'}"
            new_control = f"New in control: {self.in_control.name if self.in_control else 'Neither'}"
            turn_result = f"{initial_control}\n{card_info}\n{resolution_result.message}\n{new_control}\n"
            
            # Check for special situations based on wrestler positions
            if self.in_control:  # Only check if someone is in control
                # Check for PIN opportunity
                if get_space_type(self.in_control.position) == "PIN":
                    pin_result = self._attempt_pin()
                    turn_result += f"\n{pin_result.message}"
                    
                    if "wins by pinfall" in pin_result.message:
                        self.game_over = True
                        self._trigger_event(GameEvent.MATCH_ENDED, {
                            "winner": self.in_control.name,
                            "method": "pinfall"
                        })
                        return GameResult(True, turn_result, {"match_ended": True})
                        
                # Check for FINISHER opportunity
                elif self.in_control.position == 15:  # FINISHER space
                    finisher_result = self._attempt_finisher(self.in_control)
                    turn_result += f"\n{finisher_result.message}"
                    
                    if "They win the match" in finisher_result.message:
                        self.game_over = True
                        self._trigger_event(GameEvent.MATCH_ENDED, {
                            "winner": self.in_control.name,
                            "method": "finisher"
                        })
                        return GameResult(True, turn_result, {"match_ended": True})
            
            # Keep wrestlers within valid position range (0-15)
            for wrestler in [self.favored_wrestler, self.underdog_wrestler]:
                if wrestler and wrestler.position > 15:
                    wrestler.position = 15
                elif wrestler and wrestler.position < 0:
                    wrestler.position = 0
            
            return GameResult(True, turn_result)
            
        except Exception as e:
            logger.error(f"Error during turn: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error during turn: {e}")

    def _attempt_finisher(self, wrestler: Wrestler) -> GameResult:
        """Attempt a finisher move with the given wrestler"""
        if not wrestler.finisher:
            return GameResult(False, f"{wrestler.name} doesn't have a finisher move defined.")
        
        try:
            result = f"{wrestler.name} attempts their finisher move: {wrestler.finisher['name']}!\n"
            roll = roll_d66()
            result += f"Dice roll: {roll}\n"
            
            # Get the range as a proper tuple of integers
            finisher_range = wrestler.finisher.get('range', (11, 33))
            if isinstance(finisher_range, (list, tuple)):
                range_start, range_end = finisher_range
            else:  # Handle string format like "11-45"
                parts = str(finisher_range).split('-')
                range_start, range_end = int(parts[0]), int(parts[1])
            
            if range_start <= roll <= range_end:
                result += f"{wrestler.name}'s finisher is successful! They win the match!\n"
                self.game_over = True
                
                self._trigger_event(GameEvent.FINISHER_ATTEMPTED, {
                    "wrestler": wrestler.name,
                    "finisher": wrestler.finisher['name'],
                    "roll": roll,
                    "success": True
                })
                
                return GameResult(True, result, {"match_ended": True})
            else:
                result += f"{wrestler.name}'s finisher failed. They move back to position 9.\n"
                wrestler.position = 9
                
                self._trigger_event(GameEvent.FINISHER_ATTEMPTED, {
                    "wrestler": wrestler.name,
                    "finisher": wrestler.finisher['name'],
                    "roll": roll,
                    "success": False
                })
                
                return GameResult(True, result)
                
        except Exception as e:
            logger.error(f"Error attempting finisher: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error attempting finisher: {e}")

    def _attempt_pin(self) -> GameResult:
        """Attempt a pin with the currently advantaged wrestler"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot attempt pin: wrestlers not set.")
            
        try:
            # Determine who is pinning (wrestler with higher position)
            if self.favored_wrestler.position >= self.underdog_wrestler.position:
                pinner = self.favored_wrestler
                defender = self.underdog_wrestler
            else:
                pinner = self.underdog_wrestler
                defender = self.favored_wrestler
            
            kick_out_range = get_pin_range(defender.tv_grade)
            result = f"{pinner.name} attempts a pin on {defender.name}!\n"
            result += f"{defender.name}'s kick out range (TV Grade {defender.tv_grade}): {kick_out_range.start}-{kick_out_range.stop - 1}\n"
            
            pin_data = {
                "pinner": pinner.name,
                "defender": defender.name,
                "defender_tv_grade": defender.tv_grade,
                "kick_out_range": f"{kick_out_range.start}-{kick_out_range.stop - 1}",
                "counts": []
            }
            
            # Three count attempt
            for count in range(1, 4):
                roll = roll_d66()
                result += f"Count {count}: {defender.name} rolled {roll}\n"
                pin_data["counts"].append({"count": count, "roll": roll, "kicked_out": roll in kick_out_range})
                
                if roll in kick_out_range:
                    result += f"{defender.name} kicks out at {count}!\n"
                    pin_data["success"] = False
                    self._trigger_event(GameEvent.PIN_ATTEMPTED, pin_data)
                    return GameResult(True, result, {"pin_success": False})
            
            # If we get here, pin was successful
            result += f"{defender.name} fails to kick out. {pinner.name} wins by pinfall!\n"
            pin_data["success"] = True
            self._trigger_event(GameEvent.PIN_ATTEMPTED, pin_data)
            self.game_over = True
            return GameResult(True, result, {"pin_success": True, "match_ended": True})
            
        except Exception as e:
            logger.error(f"Error attempting pin: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error attempting pin: {e}")
        
    def _resolve_card(self, card: Card) -> GameResult:
        """Resolve a card's effects based on its type"""
        result = f"Card drawn: {card.type} ({'Control' if card.control else 'No Control'})"
        
        try:
            # Handle in-control cards first
            if card.control and self.in_control:
                return self._resolve_in_control_card(card)
            
            # Handle different card types
            card_type = card.type.lower()
            
            if card_type == "tv":
                return self._resolve_tv_card(card)
            elif card_type == "grudge":
                return self._resolve_grudge_card(card)
            elif card_type == "specialty":
                return self._resolve_specialty_card(card)
            elif card_type == "trailing":
                return self._resolve_trailing_card(card)
            elif card_type == "wild card":
                return self._resolve_wild_card(card)
            elif card_type == "helped":
                return self._resolve_helped_card(card)
            elif card_type == "highlight reel":
                return self._resolve_highlight_reel(card)
            elif card_type == "test of strength":
                return self._resolve_test_of_strength(card)
            elif card_type == "signature":
                return self._resolve_signature_card(card)
            elif card_type == "ref bump":
                return GameResult(True, "Ref Bump card drawn. This feature will be implemented in a future update.")
            elif card_type == "title holder":
                return self._resolve_title_holder_card(card)
            else:
                # Skill-specific cards (Agile, Strong, etc.)
                # Check if the card has submission text
                if card.is_submission:
                    favored_can_use = self.favored_wrestler.can_use_skill(card_type, self.favored_wrestler.position)
                    underdog_can_use = self.underdog_wrestler.can_use_skill(card_type, self.underdog_wrestler.position)
                    
                    skill_info = f"Checking if wrestlers can use {card_type} submission:\n"
                    skill_info += f"{self.favored_wrestler.name} can use: {favored_can_use}\n"
                    skill_info += f"{self.underdog_wrestler.name} can use: {underdog_can_use}\n"
                    
                    if favored_can_use and underdog_can_use:
                        skill_info += "Both wrestlers can use this submission. Using tiebreaker.\n"
                        tie_winner = self._resolve_tiebreaker_without_move(card)
                        submission_result = self._resolve_submission_card(card, tie_winner)
                        return GameResult(True, skill_info + submission_result.message)
                    elif favored_can_use:
                        submission_result = self._resolve_submission_card(card, self.favored_wrestler)
                        return GameResult(True, skill_info + submission_result.message)
                    elif underdog_can_use:
                        submission_result = self._resolve_submission_card(card, self.underdog_wrestler)
                        return GameResult(True, skill_info + submission_result.message)
                    else:
                        return GameResult(True, skill_info + "Neither wrestler can use this submission. No points scored.")
                else:
                    return self._resolve_skill_card(card)
                    
        except Exception as e:
            logger.error(f"Error resolving card: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error resolving card: {e}")

    def _resolve_in_control_card(self, card: Card) -> GameResult:
        """Resolve a card that requires a wrestler to be in control"""
        if not self.in_control:
            return GameResult(False, "No wrestler is in control. Cannot resolve in-control card.")
            
        result = f"In-control card ({card.type}) for {self.in_control.name}:\n"
        movement_result = self._move_wrestler(self.in_control, card)
        return GameResult(True, result + movement_result.message)

    def _resolve_grudge_card(self, card: Card) -> GameResult:
        """Resolve a Grudge card based on wrestler Grudge grades"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
            
        favored_grudge = self.favored_wrestler.grudge_grade
        underdog_grudge = self.underdog_wrestler.grudge_grade
        
        result = f"Comparing Grudge Grades: {self.favored_wrestler.name} ({favored_grudge}) vs {self.underdog_wrestler.name} ({underdog_grudge})\n"
        
        # Compare absolute values for grudge comparison (negative values count the same)
        if abs(favored_grudge) > abs(underdog_grudge):
            movement_result = self._move_wrestler(self.favored_wrestler, card)
            return GameResult(True, result + movement_result.message)
        elif abs(underdog_grudge) > abs(favored_grudge):
            movement_result = self._move_wrestler(self.underdog_wrestler, card)
            return GameResult(True, result + movement_result.message)
        else:
            result += "Grudge Grades are equal. Using tiebreaker.\n"
            tiebreaker_result = self._resolve_tiebreaker(card)
            return GameResult(True, result + tiebreaker_result.message)

    def _resolve_helped_card(self, card: Card) -> GameResult:
        """Resolve a Helped card based on allies in the Hot Box"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
        
        # Determine which wrestler has help (from Hot Box)
        favored_has_help = self.favored_ally is not None
        underdog_has_help = self.underdog_ally is not None
        
        if favored_has_help and underdog_has_help:
            # Both have help, use tiebreaker
            result = "Both wrestlers have help. Using tiebreaker.\n"
            winner = self._resolve_tiebreaker_without_move(card)
            ally = self.favored_ally if winner == self.favored_wrestler else self.underdog_ally
            
            helped_result = self._helped_card_logic(card, winner, ally)
            self.in_control = winner
            return GameResult(True, result + helped_result)
        elif favored_has_help:
            helped_result = self._helped_card_logic(card, self.favored_wrestler, self.favored_ally)
            self.in_control = self.favored_wrestler
            return GameResult(True, helped_result)
        elif underdog_has_help:
            helped_result = self._helped_card_logic(card, self.underdog_wrestler, self.underdog_ally)
            self.in_control = self.underdog_wrestler
            return GameResult(True, helped_result)
        else:
            return GameResult(True, "Neither wrestler has outside help. No points scored.")

    def _helped_card_logic(self, card: Card, wrestler: Wrestler, ally: Optional[Wrestler] = None) -> str:
        """Internal helper function to implement Helped card logic"""
        result = f"{wrestler.name} receives outside help"
        
        if ally:
            result += f" from {ally.name}"
        
        # If the card has points, apply them
        if card.points is not None and card.points != "" and (
            isinstance(card.points, (int, float, str)) or 
            (isinstance(card.points, dict) and wrestler.tv_grade in card.points)
        ):
            points = card.get_points(wrestler.tv_grade)
            old_position = wrestler.position
            wrestler.score(points)
            result += f". They score {points} points and move to position {wrestler.position} (from {old_position})."
            wrestler.last_card_scored = True
            
            self._trigger_event(GameEvent.WRESTLER_MOVED, {
                "wrestler": wrestler.name,
                "old_position": old_position,
                "new_position": wrestler.position,
                "points": points,
                "card_type": card.type
            })
            
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

    def _resolve_highlight_reel(self, card: Card) -> GameResult:
        """Resolve a Highlight Reel card (placeholder for future implementation)"""
        if card.text:
            result = f"Highlight Reel card: {card.text}\n"
            result += "Highlight Reel functionality will be implemented in a future update."
            return GameResult(True, result)
        else:
            return GameResult(True, "Highlight Reel card drawn, but no text specified.")

    def _resolve_skill_card(self, card: Card) -> GameResult:
        """Resolve a skill-based card (Agile, Strong, etc.)"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
            
        favored_can_use = self.favored_wrestler.can_use_skill(card.type, self.favored_wrestler.position)
        underdog_can_use = self.underdog_wrestler.can_use_skill(card.type, self.underdog_wrestler.position)

        result = f"Checking if wrestlers can use {card.type}:\n"
        result += f"{self.favored_wrestler.name} can use: {favored_can_use}\n"
        result += f"{self.underdog_wrestler.name} can use: {underdog_can_use}\n"

        if favored_can_use and underdog_can_use:
            result += "Both wrestlers can use this skill. Using tiebreaker.\n"
            tiebreaker_result = self._resolve_tiebreaker(card)
            return GameResult(True, result + tiebreaker_result.message)
        elif favored_can_use:
            movement_result = self._move_wrestler(self.favored_wrestler, card)
            return GameResult(True, result + movement_result.message)
        elif underdog_can_use:
            movement_result = self._move_wrestler(self.underdog_wrestler, card)
            return GameResult(True, result + movement_result.message)
        else:
            return GameResult(True, result + "Neither wrestler can use this skill. No points scored.")

    def _resolve_specialty_card(self, card: Card, in_control_wrestler: Optional[Wrestler] = None) -> GameResult:
        """Resolve a specialty card based on wrestler specialty moves"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
            
        result = "Specialty card drawn. "
        
        if in_control_wrestler:
            if in_control_wrestler.has_specialty():
                movement_result = self._move_wrestler(in_control_wrestler, card)
                return GameResult(True, result + movement_result.message)
            else:
                other_wrestler = self.underdog_wrestler if in_control_wrestler == self.favored_wrestler else self.favored_wrestler
                if other_wrestler.has_specialty():
                    movement_result = self._move_wrestler(other_wrestler, card)
                    return GameResult(True, result + movement_result.message)
                else:
                    return GameResult(True, result + "Neither wrestler has a Specialty defined. No points scored.")
        
        if self.favored_wrestler.has_specialty() and self.underdog_wrestler.has_specialty():
            result += "Both wrestlers have specialties. Using tiebreaker.\n"
            tiebreaker_result = self._resolve_tiebreaker(card)
            return GameResult(True, result + tiebreaker_result.message)
        elif self.favored_wrestler.has_specialty():
            movement_result = self._move_wrestler(self.favored_wrestler, card)
            return GameResult(True, result + movement_result.message)
        elif self.underdog_wrestler.has_specialty():
            movement_result = self._move_wrestler(self.underdog_wrestler, card)
            return GameResult(True, result + movement_result.message)
        else:
            return GameResult(True, result + "Neither wrestler has a Specialty defined. No points scored.")

    def _resolve_submission_card(self, card: Card, wrestler: Wrestler) -> GameResult:
        """Resolve a submission move by a wrestler"""
        if not wrestler:
            return GameResult(False, "Cannot resolve submission: wrestler not specified.")
            
        opponent = self.underdog_wrestler if wrestler == self.favored_wrestler else self.favored_wrestler
        if not opponent:
            return GameResult(False, "Cannot resolve submission: opponent not found.")
        
        result = f"{wrestler.name} attempts a submission move!\n"

        try:
            # Initial points
            points_scored = card.get_points(wrestler.tv_grade)
            old_position = wrestler.position
            wrestler.score(points_scored)
            result += f"{wrestler.name} scores {points_scored} point(s). Position: {wrestler.position}\n"
            
            # Trigger movement event
            self._trigger_event(GameEvent.WRESTLER_MOVED, {
                "wrestler": wrestler.name,
                "old_position": old_position,
                "new_position": wrestler.position,
                "points": points_scored,
                "card_type": "Submission"
            })
            
            # Determine break threshold based on opponent's strength
            opponent_is_strong = opponent.has_skill('strong') or opponent.has_skill('powerful')
            break_threshold = 4 if opponent_is_strong else 3
            
            submission_data = {
                "attacker": wrestler.name,
                "defender": opponent.name,
                "break_threshold": break_threshold,
                "rounds": []
            }
            
            # Continue until opponent breaks free
            rounds = 0
            while True:
                rounds += 1
                roll = roll_d6()
                result += f"{opponent.name} attempts to break free (roll: {roll}, needs {break_threshold} or less).\n"
                submission_data["rounds"].append({"roll": roll, "broke_free": roll <= break_threshold})
                
                if roll <= break_threshold:
                    result += f"{opponent.name} breaks the hold after {rounds} rounds.\n"
                    break
                else:
                    old_position = wrestler.position
                    wrestler.score(1)
                    result += f"{wrestler.name} maintains the hold and scores an additional point. Position: {wrestler.position}\n"
                    
                    # Trigger movement event for additional point
                    self._trigger_event(GameEvent.WRESTLER_MOVED, {
                        "wrestler": wrestler.name,
                        "old_position": old_position,
                        "new_position": wrestler.position,
                        "points": 1,
                        "card_type": "Submission Continuation"
                    })
            
            # Set the wrestler who scored as being in control
            wrestler.last_card_scored = True
            self.in_control = wrestler
            
            return GameResult(True, result, {"submission_data": submission_data})
            
        except Exception as e:
            logger.error(f"Error resolving submission: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error during submission: {e}")

    def _resolve_signature_card(self, card: Card) -> GameResult:
        """Resolve a Signature move based on the last card scored"""
        if self.in_control and self.in_control.last_card_scored:
            roll = roll_d6()
            old_position = self.in_control.position
            self.in_control.score(roll)
            
            result = f"{self.in_control.name} used a Signature move and moved from position {old_position} to {self.in_control.position} (d6 roll: {roll})"
            
            # Trigger movement event
            self._trigger_event(GameEvent.WRESTLER_MOVED, {
                "wrestler": self.in_control.name,
                "old_position": old_position,
                "new_position": self.in_control.position,
                "points": roll,
                "card_type": "Signature"
            })
            
            return GameResult(True, result)
        else:
            return GameResult(True, "No wrestler eligible for Signature move. No points scored.")

    def _resolve_test_of_strength(self, card: Card) -> GameResult:
        """Resolve a Test of Strength between two wrestlers"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
        
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
            return GameResult(True, result + "Both wrestlers must have STRONG or POWERFUL skills. No points scored.")
        
        result += "Both wrestlers qualify for Test of Strength.\n"

        tos_data = {
            "face_wrestler": face_wrestler.name,
            "heel_wrestler": heel_wrestler.name,
            "rounds": []
        }
        
        # Roll until ref breaks
        rounds = 0
        while True:
            rounds += 1
            roll = roll_d6()
            result += f"Test of Strength roll {rounds}: {roll}\n"
            
            round_data = {"roll": roll}
            
            if roll <= 2:
                old_position = face_wrestler.position
                face_wrestler.score(1)
                result += f"{face_wrestler.name} wins the exchange and scores 1 point. Position: {face_wrestler.position}\n"
                self.in_control = face_wrestler
                round_data["winner"] = face_wrestler.name
                
                # Trigger movement event
                self._trigger_event(GameEvent.WRESTLER_MOVED, {
                    "wrestler": face_wrestler.name,
                    "old_position": old_position,
                    "new_position": face_wrestler.position,
                    "points": 1,
                    "card_type": "Test of Strength"
                })
                
            elif roll <= 4:
                result += "Referee breaks up the Test of Strength. No points scored.\n"
                round_data["result"] = "ref_break"
                tos_data["rounds"].append(round_data)
                break
            else:  # 5-6
                old_position = heel_wrestler.position
                heel_wrestler.score(1)
                result += f"{heel_wrestler.name} wins the exchange and scores 1 point. Position: {heel_wrestler.position}\n"
                self.in_control = heel_wrestler
                round_data["winner"] = heel_wrestler.name
                
                # Trigger movement event
                self._trigger_event(GameEvent.WRESTLER_MOVED, {
                    "wrestler": heel_wrestler.name,
                    "old_position": old_position,
                    "new_position": heel_wrestler.position,
                    "points": 1,
                    "card_type": "Test of Strength"
                })
            
            tos_data["rounds"].append(round_data)
            
            # Check if ref breaks after scoring
            if rounds >= 3:  # Maximum 3 rounds for simplicity
                result += "Referee breaks up the Test of Strength after multiple exchanges.\n"
                break
                
            break_roll = roll_d6()
            if break_roll <= 4:
                result += f"Referee breaks up the Test of Strength (roll: {break_roll}).\n"
                break
        
        return GameResult(True, result, {"test_of_strength": tos_data})

    def _resolve_tiebreaker(self, card: Card) -> GameResult:
        """Resolve a tiebreaker between wrestlers and move the winner"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve tiebreaker: wrestlers not set.")
            
        # First tiebreaker: trailing wrestler gets the move
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            result = f"Tiebreaker: {self.favored_wrestler.name} is trailing and wins the tiebreaker.\n"
            movement_result = self._move_wrestler(self.favored_wrestler, card)
            return GameResult(True, result + movement_result.message)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            result = f"Tiebreaker: {self.underdog_wrestler.name} is trailing and wins the tiebreaker.\n"
            movement_result = self._move_wrestler(self.underdog_wrestler, card)
            return GameResult(True, result + movement_result.message)
        
        # Second tiebreaker: favored wrestler wins ties
        result = f"Tiebreaker: Wrestlers are tied. {self.favored_wrestler.name} wins as the favored wrestler.\n"
        movement_result = self._move_wrestler(self.favored_wrestler, card)
        return GameResult(True, result + movement_result.message)

    def _resolve_tiebreaker_without_move(self, card: Card) -> Wrestler:
        """Determine the winner of a tiebreaker without moving them"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return None
            
        # First tiebreaker: trailing wrestler gets the move
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.favored_wrestler
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.underdog_wrestler
        
        # Second tiebreaker: favored wrestler wins ties
        return self.favored_wrestler
        
    def _resolve_title_holder_card(self, card: Card) -> GameResult:
        """Resolve a Title Holder card if the in-control wrestler holds a title"""
        if not self.in_control:
            return GameResult(False, "No wrestler is in control. Cannot resolve Title Holder card.")
            
        # Check if the wrestler has the title_holder attribute
        is_title_holder = getattr(self.in_control, 'is_title_holder', False)
        
        if not is_title_holder:
            return GameResult(True, f"{self.in_control.name} is not a title holder. No points scored.")
        
        # Only title holders can use this card
        movement_result = self._move_wrestler(self.in_control, card)
        return movement_result
    
    def _resolve_trailing_card(self, card: Card) -> GameResult:
        """Resolve a Trailing card for the wrestler with lower position"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
            
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            result = f"{self.favored_wrestler.name} is trailing and can use the Trailing card.\n"
            movement_result = self._move_wrestler(self.favored_wrestler, card)
            return GameResult(True, result + movement_result.message)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            result = f"{self.underdog_wrestler.name} is trailing and can use the Trailing card.\n"
            movement_result = self._move_wrestler(self.underdog_wrestler, card)
            return GameResult(True, result + movement_result.message)
        else:
            # If positions are equal, the underdog is considered trailing
            if self.favored_wrestler.position == self.underdog_wrestler.position:
                result = f"Wrestlers are tied. {self.underdog_wrestler.name} can use the Trailing card as the underdog.\n"
                movement_result = self._move_wrestler(self.underdog_wrestler, card)
                return GameResult(True, result + movement_result.message)
            else:
                return GameResult(True, "Neither wrestler is trailing. No points scored.")
                
    def _resolve_tv_card(self, card: Card) -> GameResult:
        """Resolve a TV card based on wrestler TV grades"""
        if not self.favored_wrestler or not self.underdog_wrestler:
            return GameResult(False, "Cannot resolve card: wrestlers not set.")
            
        favored_grade = self.favored_wrestler.tv_grade
        underdog_grade = self.underdog_wrestler.tv_grade
        
        result = f"Comparing TV Grades: {self.favored_wrestler.name} ({favored_grade}) vs {self.underdog_wrestler.name} ({underdog_grade})\n"
        
        comparison = compare_tv_grades(favored_grade, underdog_grade)
        
        if comparison > 0:  # favored has better grade
            movement_result = self._move_wrestler(self.favored_wrestler, card)
            return GameResult(True, result + movement_result.message)
        elif comparison < 0:  # underdog has better grade
            movement_result = self._move_wrestler(self.underdog_wrestler, card)
            return GameResult(True, result + movement_result.message)
        else:  # equal grades
            result += "TV Grades are equal. Using tiebreaker.\n"
            tiebreaker_result = self._resolve_tiebreaker(card)
            return GameResult(True, result + tiebreaker_result.message)
            
    def _resolve_wild_card(self, card: Card) -> GameResult:
        """Resolve a Wild Card (placeholder for future implementation)"""
        if card.text:
            result = f"Wild Card: {card.text}\n"
            result += "Wild Card functionality will be implemented in a future update."
            return GameResult(True, result)
        else:
            return GameResult(True, "Wild Card drawn, but no text specified.")
            
    def _move_wrestler(self, wrestler: Wrestler, card: Card) -> GameResult:
        """Move a wrestler based on card points and update the in-control wrestler"""
        if not wrestler:
            return GameResult(False, "Cannot move: wrestler not specified.")
        
        try:
            # Determine points based on card type
            if card.type.lower() == "tv":
                points = card.get_points(wrestler.tv_grade)
            elif card.type.lower() == "specialty":
                points = wrestler.specialty_points
            elif card.type.lower() == "signature":
                points = roll_d6()
            else:
                points = card.get_points(wrestler.tv_grade)
            
            # Store original position for tracking
            original_position = wrestler.position
            
            # Apply points and update position
            wrestler.score(points)
            
            # Construct result message
            result = f"{wrestler.name} used {card.type} "
            if card.type.lower() == "specialty" and wrestler.specialty:
                result += f"({wrestler.specialty.get('name', 'Unnamed Specialty')}) "
            
            result += f"and moved from position {original_position} to {wrestler.position} (+{points} points)"
            
            # Update control state if points were scored
            if points > 0:
                self.in_control = wrestler
                wrestler.last_card_scored = True
                result += f"\n{wrestler.name} is now in control."
            
            # Trigger event for wrestler movement
            self._trigger_event(GameEvent.WRESTLER_MOVED, {
                "wrestler": wrestler.name,
                "old_position": original_position,
                "new_position": wrestler.position,
                "points": points,
                "card_type": card.type
            })
            
            return GameResult(True, result, {
                "wrestler": wrestler.name,
                "old_position": original_position,
                "new_position": wrestler.position,
                "points": points
            })
            
        except Exception as e:
            logger.error(f"Error moving wrestler: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error moving wrestler: {e}")
            
    def post_match_roll(self) -> GameResult:
        """Execute the post-match dice roll for storyline development"""
        try:
            d6_roll = roll_d6()
            d66_roll = roll_d66()
            
            # The actual implementation would involve more detailed tables
            # This is a placeholder for the future highlight reel implementation
            if d6_roll <= 4:
                result = f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'X'"
            else:
                # Ask for the winner since we need to know who won
                # In a real implementation, this would be based on the match state
                #winner = input("Did the Face win? (yes/no): ").lower().startswith('y')
                winner = "Face"  # Default for now
                if winner == "Face":
                    result = f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Face won. Use Highlight Reel 'T'"
                else:
                    result = f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Heel won. Use Highlight Reel 'U'"
            
            return GameResult(True, result, {"d6_roll": d6_roll, "d66_roll": d66_roll})
        except Exception as e:
            logger.error(f"Error in post-match roll: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error in post-match roll: {e}")

    def pre_match_roll(self) -> GameResult:
        """Execute the pre-match dice roll for storyline development"""
        try:
            d6_roll = roll_d6()
            d66_roll = roll_d66()
            
            # The actual implementation would involve more detailed tables
            # This is a placeholder for the future highlight reel implementation
            if d6_roll <= 4:
                result = f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'O'"
            else:
                result = f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'R'"
            
            return GameResult(True, result, {"d6_roll": d6_roll, "d66_roll": d66_roll})
        except Exception as e:
            logger.error(f"Error in pre-match roll: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error in pre-match roll: {e}")

    def set_wrestler_position(self, wrestler: Wrestler, position: int) -> GameResult:
        """Manually set a wrestler's position on the board"""
        if not wrestler:
            return GameResult(False, "Cannot set position: wrestler not specified.")
        
        try:
            old_position = wrestler.position
            # Ensure position is within valid range (0-15)
            new_position = min(max(0, position), 15)
            wrestler.position = new_position
            
            # Trigger event
            self._trigger_event(GameEvent.WRESTLER_MOVED, {
                "wrestler": wrestler.name,
                "old_position": old_position,
                "new_position": new_position,
                "points": new_position - old_position,
                "card_type": "Manual Position Set"
            })
            
            return GameResult(True, f"{wrestler.name}'s position set to {new_position}")
        except Exception as e:
            logger.error(f"Error setting wrestler position: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error setting wrestler position: {e}")

    def set_in_control(self, wrestler_name: Optional[str]) -> GameResult:
        """Manually set which wrestler is in control"""
        try:
            previous_control = self.in_control
            
            if not wrestler_name or wrestler_name.lower() == "none" or wrestler_name.lower() == "neither":
                self.in_control = None
                result = "Control set to: Neither wrestler"
            else:
                wrestler = self.wrestler_manager.get_wrestler(wrestler_name)
                if not wrestler:
                    return GameResult(False, f"Wrestler '{wrestler_name}' not found")
                
                self.in_control = wrestler
                result = f"Control set to: {wrestler.name}"
            
            # Trigger event
            self._trigger_event(GameEvent.IN_CONTROL_CHANGED, {
                "previous": previous_control.name if previous_control else "None",
                "current": self.in_control.name if self.in_control else "None"
            })
            
            return GameResult(True, result)
        except Exception as e:
            logger.error(f"Error setting in control: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error setting in control: {e}")
            
    def update_wrestler_grade(self, wrestler_name: str, grade_type: str, new_value: Union[str, int]) -> GameResult:
        """Update a wrestler's TV Grade or Grudge Grade"""
        try:
            result = self.wrestler_manager.update_wrestler_grade(wrestler_name, grade_type, new_value)
            return GameResult(True, result)
        except Exception as e:
            logger.error(f"Error updating wrestler grade: {e}")
            self._trigger_event(GameEvent.ERROR_OCCURRED, {"error": str(e)})
            return GameResult(False, f"Error updating wrestler grade: {e}")