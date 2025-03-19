# GUI Update Implementation Steps

## Overview

The current `game_gui.py` needs to be updated to work with our refactored game logic. This document outlines the specific steps needed to integrate the new backend while maintaining the existing user interface.

## Step 1: Update Imports and Class Structure

```python
# Current imports
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext

# New imports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from typing import Dict, List, Optional, Union, Any

from game_logic import Game
from game_utilities import logger, format_log_message
```

## Step 2: Update Initialization

Update the `__init__` method to work with our new game structure:

```python
def __init__(self, master, game):
    self.master = master
    self.game = game
    
    # Initialize all variables
    self.favored_var = tk.StringVar()
    self.underdog_var = tk.StringVar()
    self.favored_ally_var = tk.StringVar()
    self.favored_foe_var = tk.StringVar()
    self.underdog_ally_var = tk.StringVar()
    self.underdog_foe_var = tk.StringVar()
    self.grudge1_var = tk.StringVar()
    self.grudge2_var = tk.StringVar()
    self.in_control_var = tk.StringVar(value="Neither")
    
    # Initialize dropdown attributes
    self.favored_dropdown = None
    self.underdog_dropdown = None
    self.favored_ally_dropdown = None
    self.favored_foe_dropdown = None
    self.underdog_ally_dropdown = None
    self.underdog_foe_dropdown = None
    self.grudge1_dropdown = None
    self.grudge2_dropdown = None
    
    # Set up the GUI components
    self.setup_gui()
    self.setup_match_controls()
    self.setup_hot_box()
    self.setup_grade_update_controls()
    self.update_wrestler_dropdowns()
    
    logger.info("GUI initialized")
```

## Step 3: Update Wrestler Selection Methods

```python
def update_favored_wrestler(self, event):
    try:
        selected_name = self.favored_var.get()
        wrestler = self.game.wrestler_manager.get_wrestler(selected_name)
        if wrestler:
            self.game.favored_wrestler = wrestler
            self.update_display()
            self.update_hot_box_dropdowns()
            logger.info(f"Favored wrestler set to {selected_name}")
    except Exception as e:
        logger.error(f"Error setting favored wrestler: {e}")
        messagebox.showerror("Error", f"Could not set favored wrestler: {e}")

def update_underdog_wrestler(self, event):
    try:
        selected_name = self.underdog_var.get()
        wrestler = self.game.wrestler_manager.get_wrestler(selected_name)
        if wrestler:
            self.game.underdog_wrestler = wrestler
            self.update_display()
            self.update_hot_box_dropdowns()
            logger.info(f"Underdog wrestler set to {selected_name}")
    except Exception as e:
        logger.error(f"Error setting underdog wrestler: {e}")
        messagebox.showerror("Error", f"Could not set underdog wrestler: {e}")
```

## Step 4: Update Play Turn Method

```python
def play_turn(self):
    try:
        if not self.game.favored_wrestler or not self.game.underdog_wrestler:
            self.add_to_log("Please select wrestlers to begin the game.")
            return
            
        result = self.game.play_turn()
        self.add_to_log(result)
        self.update_display()
        self.update_in_control_display()
        
        # Check if game is over
        if self.game.game_over:
            self.show_match_end_dialog("Match is over!")
    except Exception as e:
        logger.error(f"Error playing turn: {e}")
        self.add_to_log(f"Error occurred: {e}")
        messagebox.showerror("Error", f"Error during turn: {e}")
```

## Step 5: Update In-Control Methods

```python
def update_in_control_display(self):
    if self.game.in_control == self.game.favored_wrestler:
        control_text = "Favored"
    elif self.game.in_control == self.game.underdog_wrestler:
        control_text = "Underdog"
    else:
        control_text = "Neither"
    self.in_control_var.set(control_text)

def set_in_control(self):
    try:
        control = self.in_control_var.get()
        if control == "Favored":
            self.game.in_control = self.game.favored_wrestler
        elif control == "Underdog":
            self.game.in_control = self.game.underdog_wrestler
        else:
            self.game.in_control = None
        self.add_to_log(f"In Control manually set to: {control}")
    except Exception as e:
        logger.error(f"Error setting in control: {e}")
        messagebox.showerror("Error", f"Could not set in control: {e}")
```

## Step 6: Update Hot Box Management

```python
def get_top_grudge_wrestlers(self, count=2):
    if not self.game.favored_wrestler or not self.game.underdog_wrestler:
        return []
        
    involved_wrestlers = set([
        self.favored_var.get(),
        self.underdog_var.get(),
        self.favored_ally_var.get(),
        self.favored_foe_var.get(),
        self.underdog_ally_var.get(),
        self.underdog_foe_var.get(),
        self.grudge1_var.get(),
        self.grudge2_var.get()
    ])
    
    # Filter out empty strings
    involved_wrestlers = {name for name in involved_wrestlers if name}
    
    return self.game.get_top_grudge_wrestlers(count, list(involved_wrestlers))

def update_hot_box_dropdowns(self):
    wrestler_names = sorted([w.name for w in self.game.wrestlers])
    
    for dropdown in [self.favored_ally_dropdown, self.favored_foe_dropdown,
                      self.underdog_ally_dropdown, self.underdog_foe_dropdown]:
        if dropdown:  # Check if dropdown exists before updating
            dropdown['values'] = wrestler_names

    # Update grudge wrestler dropdowns
    top_grudge_wrestlers = self.get_top_grudge_wrestlers(2)
    if self.grudge1_dropdown:
        self.grudge1_dropdown['values'] = wrestler_names
        if top_grudge_wrestlers and len(top_grudge_wrestlers) > 0:
            self.grudge1_var.set(top_grudge_wrestlers[0].name)
    if self.grudge2_dropdown:
        self.grudge2_dropdown['values'] = wrestler_names
        if top_grudge_wrestlers and len(top_grudge_wrestlers) > 1:
            self.grudge2_var.set(top_grudge_wrestlers[1].name)
```

## Step 7: Update Match Controls

```python
def pre_match_roll(self):
    try:
        result = self.game.pre_match_roll()
        self.add_to_log(result)
    except Exception as e:
        logger.error(f"Error in pre-match roll: {e}")
        self.add_to_log(f"Error in pre-match roll: {e}")

def post_match_roll(self):
    try:
        winner = messagebox.askquestion("Winner", "Did the Face win?")
        result = self.game.post_match_roll("Face" if winner == "yes" else "Heel")
        self.add_to_log(result)
    except Exception as e:
        logger.error(f"Error in post-match roll: {e}")
        self.add_to_log(f"Error in post-match roll: {e}")
```

## Step 8: Update Grade Management

```python
def update_grade(self):
    try:
        wrestler_name = self.update_wrestler_var.get()
        grade_type = self.grade_type_var.get()
        new_value = self.new_grade_var.get()
        
        if not wrestler_name:
            messagebox.showerror("Error", "Please select a wrestler.")
            return
            
        result = self.game.update_wrestler_grade(wrestler_name, grade_type, new_value)
        self.add_to_log(result)
        self.update_display()
        self.update_wrestler_dropdowns()
    except Exception as e:
        logger.error(f"Error updating grade: {e}")
        messagebox.showerror("Error", f"Could not update grade: {e}")
```

## Step 9: Update Display Methods

```python
def update_wrestler_info(self):
    info_text = ""
    for wrestler, role in [(self.game.favored_wrestler, "Favored"), (self.game.underdog_wrestler, "Underdog")]:
        if wrestler:
            info_text += f"{role}: {wrestler.name}\n"
            info_text += f"  Position: {wrestler.position}\n"
            info_text += f"  TV Grade: {wrestler.tv_grade}\n"
            info_text += f"  Grudge Grade: {wrestler.grudge_grade}\n"
            info_text += "  Skills:\n"
            for skill, skill_type in wrestler.skills.items():
                info_text += f"    {skill.capitalize()}: {skill_type.capitalize()}\n"
            if wrestler.has_specialty():
                info_text += f"  Specialty: {wrestler.specialty['name']} ({wrestler.specialty['points']} points)\n"
            if wrestler.finisher:
                info_text += f"  Finisher: {wrestler.finisher['name']} (Range: {wrestler.finisher['range'][0]}-{wrestler.finisher['range'][1]})\n"
            info_text += "\n"
    self.wrestler_info.config(text=info_text)

def update_card_display(self):
    if self.game.current_card:
        card = self.game.current_card
        card_text = f"Move Type: {card.type}\n"
        if isinstance(card.points, dict):
            card_text += "Points: Varies by TV Grade\n"
        else:
            card_text += f"Points: {card.points}\n"
        card_text += f"In-Control: {'Yes' if card.control else 'No'}"
        if card.text:
            card_text += f"\nText: {card.text}"
        self.card_label.config(text=card_text)
    else:
        self.card_label.config(text="No card drawn yet")
```

## Step 10: Update Logging Methods

```python
def add_to_log(self, message):
    try:
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n\n")
        self.log_text.see(tk.END)  # Scroll to the bottom
        self.log_text.config(state=tk.DISABLED)
        logger.info(f"Added to log: {message[:50]}...")  # Log first 50 chars
    except Exception as e:
        logger.error(f"Error adding to log: {e}")
        # Don't show error message here to avoid potential infinite loop

def clear_log(self):
    try:
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)
        logger.info("Log cleared")
    except Exception as e:
        logger.error(f"Error clearing log: {e}")
        messagebox.showerror("Error", f"Could not clear log: {e}")
```

## Implementation Order

1. Update imports and class structure first
2. Update the initialization method
3. Update the wrestler selection methods
4. Update the turn playing and card display
5. Update Hot Box management
6. Update all other UI methods
7. Test each component individually
8. Perform integration testing

## Testing Plan

After each update, test the following:

1. Can wrestlers be selected properly?
2. Does the play turn button work correctly?
3. Is card information displayed properly?
4. Does the Hot Box update as expected?
5. Can wrestler grades be updated?
6. Does the log display messages correctly?
7. Is the game board visualized correctly?

## Error Handling Strategy

- Add try/except blocks around all methods that interact with the game logic
- Log errors with appropriate levels (error, warning, info)
- Display user-friendly error messages for critical errors
- Add validation to prevent invalid user inputs