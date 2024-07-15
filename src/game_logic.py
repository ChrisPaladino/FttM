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

    def load_and_shuffle_deck(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gamedata', 'fac_deck.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self.deck = [Card(card['move_type'], card['points'], card['specific_moves'], card.get('wrestler_in_control', False)) for card in data['deck']]
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
            return [Wrestler(**w) for w in data['wrestlers']]
        except FileNotFoundError:
            print(f"Error: wrestlers.json not found at {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in wrestlers.json")
            return []

    def move_wrestler(self, wrestler, card):
        wrestler.position = min(wrestler.position + card.points, 15)
        self.last_scorer = wrestler
        return f"{wrestler.name} used {card.move_type} and moved to position {wrestler.position}"

    def play_turn(self):
        self.current_card = self.draw_card()
        if not self.current_card:
            return "No cards available. Game cannot continue."
        
        result = ""
        result += self.resolve_card(self.current_card)
        
        if self.check_win_condition():
            winner = self.favored_wrestler if self.favored_wrestler.position >= 15 else self.underdog_wrestler
            result += f"\n{winner.name} wins the match!"
        
        return result

    def resolve_card(card, active_wrestler, opponent):
        if card.type == "TV":
            points = card.get_points(active_wrestler.tv_grade)
        elif card.type in ["Wild Card", "Highlight Reel", "Ref Bump", "Test of Strength"]:
            print(f"{card.type}: {card.text}")
            # Implement logic for these special cards
            return
        elif card.type == "Grudge":
            points = card.points  # Gold, Silver, or Bronze move
        elif card.type == "Specialty":
            points = active_wrestler.specialty_points
        elif card.type == "Signature":
            if active_wrestler.last_card_scored:
                points = card.get_points()
            else:
                points = 0
        elif card.type == "Helped":
            if card.text:
                print(f"Helped: {card.text}")
                # Implement logic for special Helped cards
                return
            else:
                points = card.points
        elif card.type == "Title Holder":
            if active_wrestler.is_title_holder:
                points = card.get_points()
            else:
                points = 0
        elif card.type == "Trailing":
            if active_wrestler.is_trailing(opponent):
                points = card.points
            else:
                points = 0
        else:  # Regular skill card
            if hasattr(active_wrestler, card.type.lower()):
                points = card.points
            else:
                points = 0

        if points:
            active_wrestler.score(points)
            print(f"{active_wrestler.name} scores {points} points with a {card.type} move!")
        else:
            print(f"{active_wrestler.name} fails to score with the {card.type} card.")

        active_wrestler.last_card_scored = bool(points)

    def resolve_tiebreaker(self, card):
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.move_wrestler(self.favored_wrestler, card)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.move_wrestler(self.underdog_wrestler, card)
        else:
            return self.move_wrestler(self.underdog_wrestler, card)  # Underdog wins ties

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
        
    def setup_game(self):
        if not self.favored_wrestler or not self.underdog_wrestler:
            print("Error: Wrestlers not selected")
            return
        self.load_and_shuffle_deck()

class Wrestler:
    def __init__(self, name="", sex="Male", height="", weight="", hometown="", tv_grade="C", grudge_grade=0, skills={}, specialty={}, finisher={}, image="placeholder.png"):
        self.name = name
        self.sex = sex
        self.height = height
        self.weight = weight
        self.hometown = hometown
        self.tv_grade = tv_grade
        self.grudge_grade = grudge_grade
        self.skills = skills
        self.specialty = specialty or {"name": "", "points": "", "type": "star"}
        self.finisher = finisher or {"name": "", "range": ""}
        self.image = image
        self.position = 0
        self.last_card_scored = False
        self.is_title_holder = False  # Set this when appropriate
    
    def is_trailing(self, opponent):
        return self.score < opponent.score