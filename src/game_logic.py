import random
import json
import os

class Wrestler:
    def __init__(self, name, tv_grade, grudge_grade, skills, finisher):
        self.name = name
        self.tv_grade = tv_grade
        self.grudge_grade = grudge_grade
        self.skills = skills
        self.finisher = finisher
        self.position = 0

class Card:
    def __init__(self, move_type, points, specific_moves):
        self.move_type = move_type
        self.points = points
        self.specific_moves = specific_moves

class Game:
    def __init__(self):
        self.favored_wrestler = None
        self.underdog_wrestler = None
        self.wrestlers = []
        self.deck = []
        self.discard_pile = []
        self.hot_box = {}
        self.wrestler_in_control = None
        self.load_wrestlers()
        self.load_deck()

    def load_wrestlers(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wrestler_file = os.path.join(current_dir, '..', 'data', 'wrestlers', 'wrestlers.json')
        with open(wrestler_file, 'r') as f:
            data = json.load(f)
            self.wrestlers = [Wrestler(**w) for w in data['wrestlers']]

    def load_deck(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        deck_file = os.path.join(current_dir, '..', 'data', 'gamedata', 'fac_deck.json')
        with open(deck_file, 'r') as f:
            data = json.load(f)
            self.deck = [Card(**c) for c in data['deck']]

    def setup_game(self):
        self.favored_wrestler, self.underdog_wrestler = random.sample(self.wrestlers, 2)
        self.wrestler_in_control = random.choice([self.favored_wrestler, self.underdog_wrestler])
        self.setup_hot_box()
        self.shuffle_deck()

    def shuffle_deck(self):
        self.deck.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.deck)   

    def setup_hot_box(self):
        available_wrestlers = [w for w in self.wrestlers if w not in [self.favored_wrestler, self.underdog_wrestler]]
        roles = ['favored_ally', 'underdog_ally', 'favored_foe', 'underdog_foe', 'high_grudge1', 'high_grudge2']
        
        for role in roles:
            if available_wrestlers:
                wrestler = random.choice(available_wrestlers)
                self.hot_box[role] = wrestler
                available_wrestlers.remove(wrestler)
            else:
                self.hot_box[role] = None

    def draw_card(self):
        if not self.deck:
            print("Reshuffling deck...")
            self.shuffle_deck()
        return self.deck.pop()

    def is_skill_usable(self, wrestler, skill):
        skill_type = wrestler.skills.get(skill)
        if skill_type == 'star':
            return True
        elif skill_type == 'circle':
            return wrestler.position in [0, 1, 2, 3, 4, 6, 8, 10]
        elif skill_type == 'square':
            return wrestler.position in [5, 7, 9, 11, 12, 13, 14]
        return False

    def apply_hot_box_effect(self, wrestler, card):
        effect = 0
        for role, hot_box_wrestler in self.hot_box.items():
            if hot_box_wrestler and card.move_type in hot_box_wrestler.skills:
                if (wrestler == self.favored_wrestler and role == 'favored_ally') or \
                   (wrestler == self.underdog_wrestler and role == 'underdog_ally'):
                    effect += 1
                elif (wrestler == self.favored_wrestler and role == 'favored_foe') or \
                     (wrestler == self.underdog_wrestler and role == 'underdog_foe'):
                    effect -= 1
                elif role in ['high_grudge1', 'high_grudge2']:
                    effect += 1
        return effect

    def resolve_move(self, card, wrestler):
        if self.is_skill_usable(wrestler, card.move_type):
            hot_box_effect = self.apply_hot_box_effect(wrestler, card)
            total_points = card.points + hot_box_effect
            wrestler.position = min(wrestler.position + total_points, 15)
            self.wrestler_in_control = wrestler
            return f"{wrestler.name} performs {random.choice(card.specific_moves)} for {total_points} points!"
        return f"{wrestler.name} couldn't perform the {card.move_type} move."

    def play_turn(self):
            try:
                card = self.draw_card()
                result = f"Card drawn: {card.move_type} (Points: {card.points})\n"
                
                # Use the card's points to move the wrestler
                self.wrestler_in_control.position = min(self.wrestler_in_control.position + card.points, 15)
                
                result += f"{self.wrestler_in_control.name} uses {card.move_type} and moves to position {self.wrestler_in_control.position}"
                
                self.discard_pile.append(card)
                
                # Switch control for demonstration
                self.wrestler_in_control = (self.favored_wrestler 
                                            if self.wrestler_in_control == self.underdog_wrestler 
                                            else self.underdog_wrestler)
                
                return result, card  # Return both the result and the card
            except Exception as e:
                return f"An error occurred: {str(e)}", None

    def check_win_condition(self):
        return self.favored_wrestler.position == 15 or self.underdog_wrestler.position == 15