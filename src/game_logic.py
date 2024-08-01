import random
import json
import os

class Card:
    def __init__(self, id, control, type, points=None, text=None):
        self.id = id
        self.control = control
        self.type = type
        self.points = points
        self.text = text
        self.is_submission = "Submission!" in (text or "")

    def get_points(self, tv_grade=None):
        if isinstance(self.points, dict):  # TV card
            return self.points.get(tv_grade, 0)
        elif self.points == "d6":
            return random.randint(1, 6)
        elif isinstance(self.points, (int, float)):
            return self.points
        return 0
    
    def __str__(self):
        return f"Card {self.id}: {self.type} ({'Control' if self.control else 'No Control'})"

class Game:
    def __init__(self):
        self.in_control_counter = 0
        self.in_control = None  # Can be "Favored", "Underdog", or None
        self.favored_wrestler = None
        self.underdog_wrestler = None
        self.wrestlers = self.load_wrestlers()
        self.deck = []
        self.discard_pile = []
        self.current_card = None
        self.load_and_shuffle_deck()
        self.game_over = False

    def attempt_finisher(self, wrestler):
        if not wrestler.finisher:
            return f"{wrestler.name} doesn't have a finisher move defined."
        
        result = f"{wrestler.name} attempts their finisher move: {wrestler.finisher['name']}!\n"
        roll = self.roll_d66()
        result += f"Dice roll: {roll}\n"
        
        if roll in range(wrestler.finisher['range'][0], wrestler.finisher['range'][1] + 1):
            result += f"{wrestler.name}'s finisher is successful! They win the match!\n"
            self.game_over = True
        else:
            result += f"{wrestler.name}'s finisher failed. They move back to position 9.\n"
            wrestler.position = 9
        
        return result

    def attempt_pin(self):
        pinner = max([self.favored_wrestler, self.underdog_wrestler], key=lambda w: w.position)
        defender = self.underdog_wrestler if pinner == self.favored_wrestler else self.favored_wrestler
        
        kick_out_range = self.get_pin_range(defender.tv_grade)
        result = f"{pinner.name} attempts a pin on {defender.name}!\n"
        result += f"{defender.name}'s kick out range (TV Grade {defender.tv_grade}): {kick_out_range.start}-{kick_out_range.stop - 1}\n"
        
        for count in range(1, 4):
            roll = self.roll_d66()
            result += f"Count {count}: {defender.name} rolled {roll}\n"
            
            if roll in kick_out_range:
                result += f"{defender.name} kicks out at {count}!\n"
                return result
        
        result += f"{defender.name} fails to kick out. {pinner.name} wins by pinfall!\n"
        self.game_over = True
        return result

    def draw_card(self):
        if not self.deck:
            print("Deck is empty. Reshuffling discard pile.")
            self.deck = self.discard_pile
            self.discard_pile = []
            random.shuffle(self.deck)
        
        if self.deck:
            card = self.deck.pop(0)
            self.discard_pile.append(card)
            return card
        else:
            print("Error: No cards available even after reshuffling.")
            return None

    def get_pin_range(self, tv_grade):
        ranges = {
            'AAA': range(11, 44),  # 11-43 inclusive
            'AA': range(11, 37),   # 11-36 inclusive
            'A': range(11, 34),    # 11-33 inclusive
            'B': range(11, 27),    # 11-26 inclusive
            'C': range(11, 24),    # 11-23 inclusive
            'D': range(11, 17),    # 11-16 inclusive
            'E': range(11, 14),    # 11-13 inclusive
            'F': range(11, 12)     # 11 only
        }
        return ranges.get(tv_grade, range(11, 12))  # Default to F range if not found

    def handle_d6_points(self, wrestler, card):
        roll = self.roll_d6()
        wrestler.score(roll)
        return f"{wrestler.name} used {card.type} and moved to position {wrestler.position} (d6 roll: {roll})"

    def load_and_shuffle_deck(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gamedata', 'fac_deck.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.deck = [Card(**card) for card in data['cards']]
            random.shuffle(self.deck)
        except FileNotFoundError:
            print(f"Error: fac_deck.json not found at {file_path}")
            self.deck = []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in fac_deck.json")
            self.deck = []

    def load_wrestlers(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wrestlers', 'wrestlers.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return [Wrestler(game=self, **w) for w in data['wrestlers']]
        except FileNotFoundError:
            print(f"Error: wrestlers.json not found at {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in wrestlers.json")
            return []

    def move_wrestler(self, wrestler, card):
        if card.type == "Specialty":
            points = int(wrestler.specialty.get('points', 0))
        elif card.type == "Signature":
            points = self.roll_d6()
        else:
            points = card.get_points(wrestler.tv_grade)
        
        if isinstance(points, str):
            try:
                points = int(points)
            except ValueError:
                if points == "d6":
                    points = self.roll_d6()
                else:
                    points = 0  # Default to 0 if we can't convert to int
        
        wrestler.score(points)
        result = f"{wrestler.name} used {card.type} "
        if card.type == "Specialty":
            result += f"({wrestler.specialty.get('name', 'Unnamed Specialty')}) "
        result += f"and moved to position {wrestler.position} (+{points} points)"

        if points > 0:
            self.in_control = wrestler  # Set the in-control wrestler only if points were scored
            result += f"\n{wrestler.name} is now in control."
        
        other_wrestler = self.underdog_wrestler if wrestler == self.favored_wrestler else self.favored_wrestler
        other_wrestler.last_card_scored = False
        wrestler.last_card_scored = True
        return result

    def play_turn(self):
        initial_control = f"Current in control: {self.in_control.name if self.in_control else 'Neither'}"
        
        self.current_card = self.draw_card()
        if not self.current_card:
            return "No cards available. Game cannot continue."
        
        card_info = f"Card drawn: {self.current_card.type} ({'Control' if self.current_card.control else 'No Control'})"
        result = self.resolve_card(self.current_card)
        
        new_control = f"New in control: {self.in_control.name if self.in_control else 'Neither'}"
        
        turn_result = f"{initial_control}\n{card_info}\n{result}\n{new_control}\n"
        
        # Check for PIN or FINISHER opportunity only if a wrestler just moved
        for wrestler in [self.favored_wrestler, self.underdog_wrestler]:
            if wrestler.last_card_scored:
                if wrestler.position in [12, 13, 14]:
                    pin_result = self.attempt_pin()
                    turn_result += f"\n{pin_result}"
                    if "wins by pinfall" in pin_result:
                        self.game_over = True
                        return turn_result
                elif wrestler.position == 15:
                    finisher_result = self.attempt_finisher(wrestler)
                    turn_result += f"\n{finisher_result}"
                    if "They win the match" in finisher_result:
                        self.game_over = True
                        return turn_result
        
        # Reset last_card_scored for both wrestlers
        self.favored_wrestler.last_card_scored = False
        self.underdog_wrestler.last_card_scored = False
        
        # Check if any wrestler has moved beyond position 15
        for wrestler in [self.favored_wrestler, self.underdog_wrestler]:
            if wrestler.position > 15:
                wrestler.position = 15
        
        return turn_result

    def post_match_roll(self, winner):
        d6_roll = self.roll_d6()
        d66_roll = self.roll_d66()
        if 1 <= d6_roll <= 4:
            return f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'X'"
        else:
            if winner == "Face":
                return f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Face won. Use Highlight Reel 'T'"
            else:
                return f"Post-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Heel won. Use Highlight Reel 'U'"

    def pre_match_roll(self):
        d6_roll = self.roll_d6()
        d66_roll = self.roll_d66()
        if 1 <= d6_roll <= 4:
            return f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'O'"
        else:
            return f"Pre-Match: Rolled d6: {d6_roll}, d66: {d66_roll}. Use Highlight Reel 'R'"

    def resolve_card(self, card, is_from_in_control=False):
        if card.control and self.in_control:
            return self.resolve_in_control_card(card)
        
        if card.type == "Specialty":    
            return self.resolve_specialty_card(card)
        elif card.type == "TV":
            return self.resolve_tv_card(card)
        elif card.type == "Signature":
            return self.resolve_signature_card(card)
        elif card.type == "Grudge":
            return self.resolve_grudge_card(card)
        elif card.type == "Trailing":
            return self.resolve_trailing_card(card)
        
        favored_can_use = self.favored_wrestler.can_use_skill(card.type, self.favored_wrestler.position)
        underdog_can_use = self.underdog_wrestler.can_use_skill(card.type, self.underdog_wrestler.position)
        
        result = f"Card type: {card.type}\n"
        result += f"Favored can use: {favored_can_use}\n"
        result += f"Underdog can use: {underdog_can_use}\n"
        
        if favored_can_use and underdog_can_use:
            result += "Both wrestlers can use this skill.\n"
            result += self.resolve_tiebreaker(card)
        elif favored_can_use:
            result += "Favored wrestler can use this skill.\n"
            result += self.move_wrestler(self.favored_wrestler, card)
        elif underdog_can_use:
            result += "Underdog wrestler can use this skill.\n"
            result += self.move_wrestler(self.underdog_wrestler, card)
        else:
            result += "Neither wrestler can use this skill. No points scored."
        
        return result

    def resolve_grudge_card(self, card, preference=None):
        favored_grudge = self.favored_wrestler.grudge_grade
        underdog_grudge = self.underdog_wrestler.grudge_grade
        result = f"Grudge card drawn.\n"
        result += f"Favored wrestler's Grudge Grade: {favored_grudge}\n"
        result += f"Underdog wrestler's Grudge Grade: {underdog_grudge}\n"
        
        if favored_grudge > underdog_grudge or (favored_grudge == underdog_grudge and preference == self.favored_wrestler):
            result += self.move_wrestler(self.favored_wrestler, card)
        elif underdog_grudge > favored_grudge or (favored_grudge == underdog_grudge and preference == self.underdog_wrestler):
            result += self.move_wrestler(self.underdog_wrestler, card)
        else:
            result += "Grudge grades are tied with no preference. Using tiebreaker.\n"
            result += self.resolve_tiebreaker(card)
        return result

    def resolve_in_control_card(self, card):
        if not self.in_control:
            return "No wrestler in control. Treating as a normal card.\n" + self.resolve_card(card, is_from_in_control=True)
        
        in_control_wrestler = self.in_control
        other_wrestler = self.underdog_wrestler if in_control_wrestler == self.favored_wrestler else self.favored_wrestler
        
        result = f"In-control card ({card.type}) for {in_control_wrestler.name}:\n"
        
        if card.type == "Specialty" or in_control_wrestler.can_use_skill(card.type, in_control_wrestler.position):
            return result + self.move_wrestler(in_control_wrestler, card)
        
        new_card = self.draw_card()
        result += f"{in_control_wrestler.name} can't use {card.type}. New card drawn: {new_card.type}\n"
        
        if new_card.type in ["TV", "Grudge", "Specialty"] or other_wrestler.can_use_skill(new_card.type, other_wrestler.position):
            return result + self.move_wrestler(other_wrestler, new_card)
        else:
            return result + f"{other_wrestler.name} can't use {new_card.type}. No points scored."
    
    def resolve_signature_card(self, card):
        if self.in_control and self.in_control.last_card_scored:
            roll = self.roll_d6()
            self.in_control.score(roll)
            return f"{self.in_control.name} used a Signature move and moved to position {self.in_control.position} (d6 roll: {roll})"
        else:
            return "No wrestler eligible for Signature move. No points scored."

    def resolve_specialty_card(self, card, in_control_wrestler=None):
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

    def resolve_submission_card(self, card, wrestler):
        result = f"{wrestler.name} attempts a submission move!\n"
        points_scored = card.get_points(wrestler.tv_grade)
        wrestler.score(points_scored)
        result += f"{wrestler.name} scores {points_scored} point(s). Position: {wrestler.position}\n"
        
        opponent = self.underdog_wrestler if wrestler == self.favored_wrestler else self.favored_wrestler
        opponent_is_strong = opponent.has_skill('strong') or opponent.has_skill('powerful')
        
        while True:
            roll = self.roll_d6()
            break_hold = 3 if not opponent_is_strong else 4
            if roll <= break_hold:
                result += f"Opponent breaks the hold with a roll of {roll}.\n"
                break
            else:
                wrestler.score(1)
                result += f"{wrestler.name} scores an additional point. Position: {wrestler.position}\n"
        
        return result

    def resolve_tiebreaker(self, card):
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return self.move_wrestler(self.favored_wrestler, card)  # Favored wins ties

    def resolve_trailing_card(self, card):
        if self.favored_wrestler.is_trailing(self.underdog_wrestler):
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.is_trailing(self.favored_wrestler):
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return "Neither wrestler is trailing. No points scored."

    def resolve_tv_card(self, card):
        tv_grades = ['AAA', 'AA', 'A', 'B', 'C', 'D', 'E']
        favored_grade = self.favored_wrestler.tv_grade
        underdog_grade = self.underdog_wrestler.tv_grade
        
        if tv_grades.index(favored_grade) < tv_grades.index(underdog_grade):
            return self.move_wrestler(self.favored_wrestler, card)
        elif tv_grades.index(underdog_grade) < tv_grades.index(favored_grade):
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return self.resolve_tiebreaker(card)

    def resolve_wrestler_in_control(self, card, favored_has_skill, underdog_has_skill):
        result = "Resolving In-Control card:\n"
        if self.in_control:
            result += f"Wrestler in control is {self.in_control.name}\n"
            if (self.in_control == self.favored_wrestler and favored_has_skill) or \
            (self.in_control == self.underdog_wrestler and underdog_has_skill):
                result += self.move_wrestler(self.in_control, card)
            else:
                new_card = self.draw_card()
                result += f"{self.in_control.name} can't use {card.type}. New card drawn: {new_card.type}\n"
                opponent = self.underdog_wrestler if self.in_control == self.favored_wrestler else self.favored_wrestler
                if new_card.type.lower() in [skill.lower() for skill in opponent.skills]:
                    result += self.move_wrestler(opponent, new_card)
                else:
                    result += "Neither wrestler could use the In-Control exchange. Play continues."
        else:
            result += "No wrestler in control, resolving as a normal card.\n"
            if favored_has_skill and underdog_has_skill:
                result += self.resolve_tiebreaker(card)
            elif favored_has_skill:
                result += self.move_wrestler(self.favored_wrestler, card)
            elif underdog_has_skill:
                result += self.move_wrestler(self.underdog_wrestler, card)
            else:
                result += "Neither wrestler has this skill. No movement."
        return result

    def roll_d6(self):
        return random.randint(1, 6)

    def roll_d66(self):
        return random.randint(1, 6) * 10 + random.randint(1, 6)
    
    def save_wrestlers(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wrestlers', 'wrestlers.json')
        data = {"wrestlers": []}
        for wrestler in self.wrestlers:
            wrestler_data = {
                "name": wrestler.name,
                "sex": wrestler.sex,
                "height": wrestler.height,
                "weight": wrestler.weight,
                "hometown": wrestler.hometown,
                "tv_grade": wrestler.tv_grade,
                "grudge_grade": wrestler.grudge_grade,
                "skills": wrestler.skills,
                "specialty": wrestler.specialty,
                "finisher": wrestler.finisher,
                "image": wrestler.image
            }
            data["wrestlers"].append(wrestler_data)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def set_in_control(self, wrestler):
        if wrestler == self.favored_wrestler:
            self.in_control = "Favored"
        elif wrestler == self.underdog_wrestler:
            self.in_control = "Underdog"
        else:
            self.in_control = None

    def set_wrestler_position(self, wrestler, position):
        if wrestler == self.favored_wrestler:
            self.favored_wrestler.position = position
        elif wrestler == self.underdog_wrestler:
            self.underdog_wrestler.position = position

    def setup_game(self):
        if not self.favored_wrestler or not self.underdog_wrestler:
            print("Error: Wrestlers not selected")
            return
        self.load_and_shuffle_deck()

    def update_wrestler_grade(self, wrestler_name, grade_type, new_value):
        wrestler = next((w for w in self.wrestlers if w.name == wrestler_name), None)
        if wrestler:
            if grade_type.upper() == "GRUDGE":
                wrestler.grudge_grade = int(new_value)
            elif grade_type.upper() == "TV":
                wrestler.tv_grade = new_value
            self.save_wrestlers()
            return f"Updated {wrestler_name}'s {grade_type} grade to {new_value}"
        return f"Wrestler {wrestler_name} not found"

class Wrestler:
    def __init__(self, game, name, sex, height, weight, hometown, tv_grade, grudge_grade, skills, specialty, finisher, image="placeholder.png"):
        self.game = game
        self.name = name
        self.sex = sex
        self.height = height
        self.weight = weight
        self.hometown = hometown
        self.tv_grade = tv_grade
        self.grudge_grade = int(grudge_grade)
        self.skills = {k.lower(): v.lower() for k, v in skills.items()}  # Convert skills to lowercase
        self.specialty = specialty
        if self.specialty and 'points' in self.specialty:
            try:
                self.specialty['points'] = int(self.specialty['points'])
            except ValueError:
                self.specialty['points'] = 0
        self.finisher = finisher
        if self.finisher and 'range' in self.finisher:
            self.finisher['range'] = tuple(map(int, self.finisher['range'].split('-')))
        self.image = image
        self.position = 0
        self.last_card_scored = False
        self.is_title_holder = False  # Set this when appropriate

    def can_use_skill(self, skill, position):
        skill = skill.lower()
        if skill == 'grudge':
            return True
        if skill in self.skills:
            skill_type = self.skills[skill]
            if position == 15:  # FINISHER space, all skills can be used
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
        return self.position < opponent.position or (self.position == opponent.position and self == self.game.underdog_wrestler)    

    def attempt_kickout(self):
        kickout_range = self.game.get_pin_range(self.tv_grade)
        result = ""
        for attempt in range(3):
            roll = self.game.roll_d66()
            kickout_success = roll in kickout_range
            result += f"{self.name} kickout attempt {attempt + 1}: Rolled {roll} ({'Success' if kickout_success else 'Fail'})\n"
            if kickout_success:
                result += f"{self.name} kicks out!\n"
                return result
        result += f"{self.name} fails to kick out.\n"
        return result

    def score(self, points):
        self.position += points
        self.position = min(self.position, 15)
        self.last_card_scored = True

    @property
    def specialty_points(self):
        return int(self.specialty.get('points', 0))