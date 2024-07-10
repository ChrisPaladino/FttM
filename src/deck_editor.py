import json
import os
import random

class FAC:
    def __init__(self, move_type, points, specific_moves, wrestler_in_control=False):
        self.move_type = move_type
        self.points = points
        self.wrestler_in_control = wrestler_in_control

def load_deck():
    file_path = os.path.join('..', 'data', 'gamedata', 'fac_deck.json')
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return [FAC(**card) for card in data['deck']]
    except FileNotFoundError:
        return []

def save_deck(deck):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, '..', 'data', 'gamedata', 'fac_deck.json')

    data = {'deck': [card.__dict__ for card in deck]}
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def add_card(deck):
    print("\nAdding a new card:")
    move_type = input("Enter move type: ")
    points = input("Enter points (enter 'd6' for random 1d6): ")
    wrestler_in_control = input("Is this a Wrestler In Control card? (y/n): ").lower() == 'y'
    
    new_card = FAC(move_type, points, wrestler_in_control)
    deck.append(new_card)
    print("Card added successfully!")

def edit_card(deck):
    print("\nEditing a card:")
    for i, card in enumerate(deck):
        print(f"{i+1}. {card.move_type}")
    
    choice = int(input("Enter the number of the card to edit: ")) - 1
    card = deck[choice]
    
    print(f"\nEditing card: {card.move_type}")
    card.move_type = input(f"Enter new move type (current: {card.move_type}): ") or card.move_type
    card.points = input(f"Enter new points (current: {card.points}): ") or card.points
    
    for i, move in enumerate(card.specific_moves):
        new_move = input(f"Enter new specific move {i+1} (current: {move}): ")
        if new_move:
            card.specific_moves[i] = new_move
    
    while len(card.specific_moves) < 6:
        new_move = input(f"Enter new specific move {len(card.specific_moves)+1}: ")
        if new_move == "":
            break
        card.specific_moves.append(new_move)
    
    wic = input(f"Is this a Wrestler In Control card? (y/n) (current: {'y' if card.wrestler_in_control else 'n'}): ")
    if wic.lower() in ['y', 'n']:
        card.wrestler_in_control = (wic.lower() == 'y')
    
    print("Card edited successfully!")

def main():
    deck = load_deck()
    
    while True:
        print("\n--- FAC Deck Editor ---")
        print("1. Add a new card")
        print("2. Edit an existing card")
        print("3. Save and exit")
        
        choice = input("Enter your choice (1-3): ")
        
        if choice == '1':
            add_card(deck)
        elif choice == '2':
            if deck:
                edit_card(deck)
            else:
                print("No cards in the deck to edit.")
        elif choice == '3':
            save_deck(deck)
            print("Deck saved. Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()