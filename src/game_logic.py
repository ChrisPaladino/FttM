import random
import json
import os

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

class Card:
    def __init__(self, move_type, points, specific_moves, wrestler_in_control=False):
        self.move_type = move_type
        self.points = points
        self.specific_moves = specific_moves
        self.wrestler_in_control = wrestler_in_control

class Game:
    def __init__(self):
        self.favored_wrestler = None
        self.underdog_wrestler = None
        self.wrestlers = self.load_wrestlers()
        self.deck = []
        self.discard_pile = []
        self.current_card = None
        self.wrestler_in_control = None
        self.load_and_shuffle_deck()

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
            self.deck = [Card(**card) for card in data['deck']]
            random.shuffle(self.deck)
        except FileNotFoundError:
            print(f"Error: fac_deck.json not found at {file_path}")
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in fac_deck.json")

    def load_wrestlers(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'wrestlers', 'wrestlers.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            wrestlers = [Wrestler(**w) for w in data['wrestlers']]
            print(f"Loaded {len(wrestlers)} wrestlers:")
            for w in wrestlers:
                print(f"  {w.name}: {w.skills}")
            return wrestlers
        except FileNotFoundError:
            print(f"Error: wrestlers.json not found at {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in wrestlers.json")
            return []
        
    def load_deck(self):
        file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gamedata', 'fac_deck.json')
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return [Card(**card) for card in data['deck']]
        except FileNotFoundError:
            print(f"Error: fac_deck.json not found at {file_path}")
            return []
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON in fac_deck.json")
            return []

    def move_wrestler(self, wrestler):
        wrestler.position = min(wrestler.position + self.current_card.points, 15)
        self.wrestler_in_control = wrestler
        return f"{wrestler.name} used {self.current_card.move_type} and moved to position {wrestler.position}"

    def resolve_wrestler_in_control(self):
        if self.wrestler_in_control.skills.get(self.current_card.move_type.lower()):
            return self.move_wrestler(self.wrestler_in_control)
        else:
            opponent = self.favored_wrestler if self.wrestler_in_control == self.underdog_wrestler else self.underdog_wrestler
            if opponent.skills.get(self.current_card.move_type.lower()):
                return self.move_wrestler(opponent)
            else:
                self.wrestler_in_control = opponent
                return f"Control switched to {opponent.name}. No movement."

    def resolve_tiebreaker(self):
        # Implement tiebreaker rules here. For now, we'll use a simple rule:
        # The wrestler who is behind gets to move. If tied, the underdog moves.
        if self.favored_wrestler.position < self.underdog_wrestler.position:
            return self.move_wrestler(self.favored_wrestler)
        elif self.underdog_wrestler.position < self.favored_wrestler.position:
            return self.move_wrestler(self.underdog_wrestler)
        else:
            return self.move_wrestler(self.underdog_wrestler)

    def setup_game(self):
        if len(self.wrestlers) < 2:
            print("Error: Not enough wrestlers to start a game")
            return
        self.favored_wrestler, self.underdog_wrestler = random.sample(self.wrestlers, 2)
        self.wrestler_in_control = random.choice([self.favored_wrestler, self.underdog_wrestler])
        self.load_and_shuffle_deck()

    def play_turn(self):
        self.current_card = self.draw_card()
        if not self.current_card:
            return "No cards available. Game cannot continue."
        
        if self.current_card.wrestler_in_control:
            return self.resolve_wrestler_in_control()
        
        favored_has_skill = self.current_card.move_type.lower() in [skill.lower() for skill in self.favored_wrestler.skills]
        underdog_has_skill = self.current_card.move_type.lower() in [skill.lower() for skill in self.underdog_wrestler.skills]
        
        if favored_has_skill and underdog_has_skill:
            return self.resolve_tiebreaker()
        elif favored_has_skill:
            return self.move_wrestler(self.favored_wrestler)
        elif underdog_has_skill:
            return self.move_wrestler(self.underdog_wrestler)
        else:
            return f"Card drawn: {self.current_card.move_type}. Neither wrestler has this skill. No movement."

    def check_win_condition(self):
        return self.favored_wrestler.position >= 15 or self.underdog_wrestler.position >= 15