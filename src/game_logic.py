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
        self.favored_wrestler = None
        self.underdog_wrestler = None
        self.wrestlers = self.load_wrestlers()
        self.deck = []
        self.discard_pile = []
        self.current_card = None
        self.last_scorer = None
        self.load_and_shuffle_deck()

    def check_win_condition(self):
        return self.favored_wrestler.position >= 15 or self.underdog_wrestler.position >= 15

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
        points = card.get_points(wrestler.tv_grade)
        if points == "d6":
            return self.handle_d6_points(wrestler, card)
        else:
            wrestler.score(points)
            self.last_scorer = wrestler
            other_wrestler = self.underdog_wrestler if wrestler == self.favored_wrestler else self.favored_wrestler
            other_wrestler.last_card_scored = False
            return f"{wrestler.name} used {card.type} and moved to position {wrestler.position} (+{points} points)"

    def play_turn(self):
        self.current_card = self.draw_card()
        if not self.current_card:
            return "No cards available. Game cannot continue."
        print(f"Current card: {self.current_card.type}, Control: {self.current_card.control}")
        result = self.resolve_card(self.current_card)
        
        if self.check_win_condition():
            winner = self.favored_wrestler if self.favored_wrestler.position >= 15 else self.underdog_wrestler
            result += f"\n{winner.name} wins the match!"
        
        return result

    def resolve_card(self, card, is_from_in_control=False):
        if card.control and not is_from_in_control:
            self.in_control_counter += 1
            print(f"In-Control card drawn. Total: {self.in_control_counter}")
        favored_has_skill = self.favored_wrestler.has_skill(card.type)
        underdog_has_skill = self.underdog_wrestler.has_skill(card.type)
        
        if card.control and not is_from_in_control:
            return self.resolve_in_control_card(card)
        
        if card.type == "Trailing":
            if self.favored_wrestler.is_trailing(self.underdog_wrestler):
                return self.move_wrestler(self.favored_wrestler, card)
            elif self.underdog_wrestler.is_trailing(self.favored_wrestler):
                return self.move_wrestler(self.underdog_wrestler, card)
            else:
                return "Neither wrester is trailing. No points scored."

        if card.type == "TV":
            return self.resolve_tv_card(card)
        elif card.type == "Grudge":
            return self.resolve_grudge_card(card)
        elif card.type == "Signature":
            return self.resolve_signature_card(card)

        if favored_has_skill and underdog_has_skill:
            if self.favored_wrestler.is_trailing(self.underdog_wrestler):
                return self.move_wrestler(self.favored_wrestler, card)
            elif self.underdog_wrestler.is_trailing(self.favored_wrestler):
                return self.move_wrestler(self.underdog_wrestler, card)
            else:
                # Underdog wins ties
                return self.move_wrestler(self.underdog_wrestler, card)
        elif favored_has_skill:
            return self.move_wrestler(self.favored_wrestler, card)
        elif underdog_has_skill:
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return f"Neither wrestler has the {card.type} skill. No points scored."

    def resolve_grudge_card(self, card):
        if self.favored_wrestler.grudge_grade > self.underdog_wrestler.grudge_grade:
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.grudge_grade > self.favored_wrestler.grudge_grade:
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return self.resolve_tiebreaker(card)

    def resolve_in_control_card(self, card):
        print(f"Resolving In-Control card: {card.type}")
        print(f"Last scorer: {self.last_scorer.name if self.last_scorer else 'None'}")
        
        if not self.last_scorer:
            return "No wrestler in control. Treating as a normal card.\n" + self.resolve_card(card, is_from_in_control=True)
        
        in_control_wrestler = self.last_scorer
        other_wrestler = self.underdog_wrestler if in_control_wrestler == self.favored_wrestler else self.favored_wrestler
        
        if in_control_wrestler.has_skill(card.type):
            return self.move_wrestler(in_control_wrestler, card)
        
        new_card = self.draw_card()
        result = f"In-control wrestler doesn't have the skill. New card drawn: {new_card.type}\n"

        if other_wrestler.has_skill(new_card.type):
            result += self.move_wrestler(other_wrestler, new_card)
            self.last_scorer = other_wrestler  # Set the other wrestler as the last scorer
        else:
            result += "Opponent doesn't have the skill either. No points scored."
        
        return result

    def resolve_signature_card(self, card):
        if self.last_scorer and self.last_scorer.last_card_scored:
            return self.handle_d6_points(self.last_scorer, card)
        else:
            return "No wrestler eligible for Signature move. No points scored."

    def resolve_tiebreaker(self, card):
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return self.move_wrestler(self.underdog_wrestler, card)  # Underdog wins ties

    def resolve_tv_card(self, card):
        favored_points = card.get_points(self.favored_wrestler.tv_grade)
        underdog_points = card.get_points(self.underdog_wrestler.tv_grade)
        if favored_points > underdog_points:
            return self.move_wrestler(self.favored_wrestler, card)
        elif underdog_points > favored_points:
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return self.resolve_tiebreaker(card)

    def resolve_wrestler_in_control(self, card, favored_has_skill, underdog_has_skill):
        result = "Resolving In-Control card:\n"
        if self.last_scorer:
            result += f"Last scorer was {self.last_scorer.name}\n"
            if (self.last_scorer == self.favored_wrestler and favored_has_skill) or \
               (self.last_scorer == self.underdog_wrestler and underdog_has_skill):
                result += self.move_wrestler(self.last_scorer, card)
            else:
                new_card = self.draw_card()
                result += f"Last scorer doesn't have the skill. New card drawn: {new_card.move_type}\n"
                opponent = self.underdog_wrestler if self.last_scorer == self.favored_wrestler else self.favored_wrestler
                if new_card.move_type.lower() in [skill.lower() for skill in opponent.skills]:
                    result += self.move_wrestler(opponent, new_card)
                else:
                    result += "Neither wrestler could use the In-Control exchange. Play continues."
        else:
            result += "No last scorer, resolving as a normal card.\n"
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

    def setup_game(self):
        if not self.favored_wrestler or not self.underdog_wrestler:
            print("Error: Wrestlers not selected")
            return
        self.load_and_shuffle_deck()

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
        self.skills = skills
        self.specialty = specialty
        self.finisher = finisher
        self.image = image
        self.position = 0
        self.last_card_scored = False
        self.is_title_holder = False  # Set this when appropriate

    def has_skill(self, skill):
        return skill.lower() in [s.lower() for s in self.skills]

    def is_trailing(self, opponent):
        return self.position < opponent.position or (self.position == opponent.position and self == self.game.underdog_wrestler)    

    def score(self, points):
        self.position += points
        self.position = min(self.position, 15)
        self.last_card_scored = True

    @property
    def specialty_points(self):
        return int(self.specialty.get('points', 0))