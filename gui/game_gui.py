"""
Face to the Mat - Game GUI
This module provides the graphical user interface for the game,
using the refactored event-based game logic.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from typing import Dict, List, Optional, Union, Any, Callable
import os

from game_logic import Game, GameEvent, GameResult
from game_utilities import logger, format_log_message

class GameEventHandler:
    """Handles game events and updates the UI accordingly"""
    
    def __init__(self, ui):
        """Initialize with reference to the UI"""
        self.ui = ui
    
    def handle_card_drawn(self, event_data: Dict):
        """Handle card drawn event"""
        self.ui.update_card_display(event_data)
    
    def handle_card_resolved(self, event_data: Dict):
        """Handle card resolution event"""
        # Update may be handled by wrestler_moved event
        pass
    
    def handle_wrestler_moved(self, event_data: Dict):
        """Handle wrestler movement event"""
        self.ui.update_board()
        self.ui.add_to_log(f"{event_data['wrestler']} moved from position {event_data['old_position']} to {event_data['new_position']} (+{event_data['points']} points)")
    
    def handle_pin_attempted(self, event_data: Dict):
        """Handle pin attempt event"""
        message = f"{event_data['pinner']} attempts a pin on {event_data['defender']}!\n"
        message += f"Kick out range: {event_data['kick_out_range']}\n"
        
        for count_data in event_data['counts']:
            message += f"Count {count_data['count']}: Roll {count_data['roll']}"
            if count_data['kicked_out']:
                message += " - Kicked out!\n"
            else:
                message += "\n"
                
        if event_data.get('success', False):
            message += f"{event_data['pinner']} wins by pinfall!"
        
        self.ui.add_to_log(message)
    
    def handle_finisher_attempted(self, event_data: Dict):
        """Handle finisher attempt event"""
        message = f"{event_data['wrestler']} attempts their finisher!\n"
        message += f"Roll: {event_data['roll']}\n"
        
        if event_data.get('success', False):
            message += f"{event_data['wrestler']} connects with their finisher and wins the match!"
        else:
            message += f"{event_data['wrestler']}'s finisher failed."
        
        self.ui.add_to_log(message)
    
    def handle_match_ended(self, event_data: Dict):
        """Handle match end event"""
        message = f"Match is over! {event_data['winner']} wins by {event_data['method']}."
        self.ui.add_to_log(message)
        self.ui.show_match_end_dialog(message)
    
    def handle_in_control_changed(self, event_data: Dict):
        """Handle change in control event"""
        previous = event_data.get('previous', 'Neither')
        current = event_data.get('current', 'Neither')
        
        if previous != current:
            message = f"Control changed from {previous} to {current}"
            self.ui.add_to_log(message)
            self.ui.update_in_control_display()
    
    def handle_hot_box_updated(self, event_data: Dict):
        """Handle Hot Box update event"""
        self.ui.update_hot_box_display()
    
    def handle_error_occurred(self, event_data: Dict):
        """Handle error event"""
        error_message = event_data.get('error', 'Unknown error')
        self.ui.add_to_log(f"ERROR: {error_message}")
        messagebox.showerror("Error", error_message)


class GameGUI:
    """Main GUI class for Face to the Mat"""
    
    def __init__(self, master, game):
        """Initialize the GUI with root window and game engine"""
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
        self.position_var = tk.StringVar()
        self.update_wrestler_var = tk.StringVar()
        self.grade_type_var = tk.StringVar(value="GRUDGE")
        self.new_grade_var = tk.StringVar()

        # Initialize dropdown attributes
        self.favored_dropdown = None
        self.underdog_dropdown = None
        self.favored_ally_dropdown = None
        self.favored_foe_dropdown = None
        self.underdog_ally_dropdown = None
        self.underdog_foe_dropdown = None
        self.grudge1_dropdown = None
        self.grudge2_dropdown = None
        self.update_wrestler_dropdown = None
        
        # Set up event handler
        self.event_handler = GameEventHandler(self)
        self._register_event_listeners()
        
        # Set up UI components
        self.setup_gui()
        self.setup_match_controls()
        self.setup_hot_box()
        self.setup_grade_update_controls()
        self.update_wrestler_dropdowns()
        
        logger.info("GUI initialized")
    
    def _register_event_listeners(self):
        """Register event listeners with the game engine"""
        self.game.add_event_listener(GameEvent.CARD_DRAWN, self.event_handler.handle_card_drawn)
        self.game.add_event_listener(GameEvent.CARD_RESOLVED, self.event_handler.handle_card_resolved)
        self.game.add_event_listener(GameEvent.WRESTLER_MOVED, self.event_handler.handle_wrestler_moved)
        self.game.add_event_listener(GameEvent.PIN_ATTEMPTED, self.event_handler.handle_pin_attempted)
        self.game.add_event_listener(GameEvent.FINISHER_ATTEMPTED, self.event_handler.handle_finisher_attempted)
        self.game.add_event_listener(GameEvent.MATCH_ENDED, self.event_handler.handle_match_ended)
        self.game.add_event_listener(GameEvent.IN_CONTROL_CHANGED, self.event_handler.handle_in_control_changed)
        self.game.add_event_listener(GameEvent.HOT_BOX_UPDATED, self.event_handler.handle_hot_box_updated)
        self.game.add_event_listener(GameEvent.ERROR_OCCURRED, self.event_handler.handle_error_occurred)
    
    def add_to_log(self, message):
        """Add a message to the game log"""
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, message + "\n\n")
            self.log_text.see(tk.END)  # Scroll to the bottom
            self.log_text.config(state=tk.DISABLED)
            logger.info(f"Added to log: {message[:50]}..." if len(message) > 50 else f"Added to log: {message}")
        except Exception as e:
            logger.error(f"Error adding to log: {e}")
            # Don't show error message here to avoid potential infinite loop
    
    def clear_log(self):
        """Clear the game log"""
        try:
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state=tk.DISABLED)
            logger.info("Log cleared")
        except Exception as e:
            logger.error(f"Error clearing log: {e}")
            messagebox.showerror("Error", f"Could not clear log: {e}")
    
    def get_top_grudge_wrestlers(self, count=2):
        """Get top wrestlers by grudge grade, excluding those already in the match"""
        try:
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
        except Exception as e:
            logger.error(f"Error getting top grudge wrestlers: {e}")
            return []

    def play_turn(self):
        """Execute a game turn"""
        try:
            if not self.game.favored_wrestler or not self.game.underdog_wrestler:
                self.add_to_log("Please select wrestlers to begin the game.")
                return
                
            result = self.game.play_turn()
            if not result.success:
                self.add_to_log(f"Error: {result.message}")
                return
                
            self.add_to_log(result.message)
            self.update_display()
            
        except Exception as e:
            logger.error(f"Error playing turn: {e}")
            self.add_to_log(f"Error occurred: {e}")
            messagebox.showerror("Error", f"Error during turn: {e}")

    def post_match_roll(self):
        """Execute post-match roll"""
        try:
            winner = messagebox.askquestion("Winner", "Did the Face win?")
            result = self.game.post_match_roll("Face" if winner == "yes" else "Heel")
            if result.success:
                self.add_to_log(result.message)
            else:
                self.add_to_log(f"Error: {result.message}")
        except Exception as e:
            logger.error(f"Error in post-match roll: {e}")
            self.add_to_log(f"Error in post-match roll: {e}")
            messagebox.showerror("Error", f"Error in post-match roll: {e}")

    def pre_match_roll(self):
        """Execute pre-match roll"""
        try:
            result = self.game.pre_match_roll()
            if result.success:
                self.add_to_log(result.message)
            else:
                self.add_to_log(f"Error: {result.message}")
        except Exception as e:
            logger.error(f"Error in pre-match roll: {e}")
            self.add_to_log(f"Error in pre-match roll: {e}")
            messagebox.showerror("Error", f"Error in pre-match roll: {e}")

    def set_in_control(self):
        """Set which wrestler is in control"""
        try:
            control = self.in_control_var.get()
            if control == "Favored":
                wrestler_name = self.favored_var.get()
            elif control == "Underdog":
                wrestler_name = self.underdog_var.get()
            else:
                wrestler_name = None
                
            result = self.game.set_in_control(wrestler_name)
            if result.success:
                self.add_to_log(result.message)
            else:
                self.add_to_log(f"Error: {result.message}")
                
        except Exception as e:
            logger.error(f"Error setting in control: {e}")
            messagebox.showerror("Error", f"Could not set in control: {e}")
    
    def setup_hot_box(self):
        """Set up the Hot Box UI panel"""
        hot_box_frame = ttk.LabelFrame(self.master, text="Hot Box", padding="10")
        hot_box_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=10)

        # Initialize all dropdown variables
        self.favored_ally_var = tk.StringVar()
        self.favored_foe_var = tk.StringVar()
        self.underdog_ally_var = tk.StringVar()
        self.underdog_foe_var = tk.StringVar()
        self.grudge1_var = tk.StringVar()
        self.grudge2_var = tk.StringVar()

        # Favored wrestler's ally and foe
        ttk.Label(hot_box_frame, text="Favored Wrestler:").grid(row=0, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(hot_box_frame, text="Ally:").grid(row=0, column=1, sticky="e", padx=5, pady=2)
        self.favored_ally_dropdown = ttk.Combobox(hot_box_frame, textvariable=self.favored_ally_var)
        self.favored_ally_dropdown.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        ttk.Label(hot_box_frame, text="Foe:").grid(row=0, column=3, sticky="e", padx=5, pady=2)
        self.favored_foe_dropdown = ttk.Combobox(hot_box_frame, textvariable=self.favored_foe_var)
        self.favored_foe_dropdown.grid(row=0, column=4, sticky="ew", padx=5, pady=2)

        # Underdog wrestler's ally and foe
        ttk.Label(hot_box_frame, text="Underdog Wrestler:").grid(row=1, column=0, sticky="e", padx=5, pady=2)
        ttk.Label(hot_box_frame, text="Ally:").grid(row=1, column=1, sticky="e", padx=5, pady=2)
        self.underdog_ally_dropdown = ttk.Combobox(hot_box_frame, textvariable=self.underdog_ally_var)
        self.underdog_ally_dropdown.grid(row=1, column=2, sticky="ew", padx=5, pady=2)

        ttk.Label(hot_box_frame, text="Foe:").grid(row=1, column=3, sticky="e", padx=5, pady=2)
        self.underdog_foe_dropdown = ttk.Combobox(hot_box_frame, textvariable=self.underdog_foe_var)
        self.underdog_foe_dropdown.grid(row=1, column=4, sticky="ew", padx=5, pady=2)

        # Grudge wrestlers
        ttk.Label(hot_box_frame, text="Grudge Wrestlers:").grid(row=2, column=0, sticky="e", padx=5, pady=2)
        self.grudge1_dropdown = ttk.Combobox(hot_box_frame, textvariable=self.grudge1_var)
        self.grudge1_dropdown.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=2)

        self.grudge2_dropdown = ttk.Combobox(hot_box_frame, textvariable=self.grudge2_var)
        self.grudge2_dropdown.grid(row=2, column=3, columnspan=2, sticky="ew", padx=5, pady=2)

        # Bind events to update functions
        self.favored_ally_dropdown.bind("<<ComboboxSelected>>", self.update_hot_box_dropdowns)
        self.favored_foe_dropdown.bind("<<ComboboxSelected>>", self.update_hot_box_dropdowns)
        self.underdog_ally_dropdown.bind("<<ComboboxSelected>>", self.update_hot_box_dropdowns)
        self.underdog_foe_dropdown.bind("<<ComboboxSelected>>", self.update_hot_box_dropdowns)
        self.grudge1_dropdown.bind("<<ComboboxSelected>>", self.update_hot_box_dropdowns)
        self.grudge2_dropdown.bind("<<ComboboxSelected>>", self.update_hot_box_dropdowns)
        
        # Setup Hot Box button
        ttk.Button(hot_box_frame, text="Update Hot Box", command=self.update_hot_box).grid(row=3, column=2, columnspan=2, pady=5)

    def update_hot_box(self):
        """Update the Hot Box in the game engine"""
        try:
            result = self.game.setup_hot_box(
                favored_ally_name=self.favored_ally_var.get() or None,
                favored_foe_name=self.favored_foe_var.get() or None,
                underdog_ally_name=self.underdog_ally_var.get() or None,
                underdog_foe_name=self.underdog_foe_var.get() or None,
                grudge_wrestler_names=[
                    name for name in [self.grudge1_var.get(), self.grudge2_var.get()]
                    if name
                ]
            )
            
            if result.success:
                self.add_to_log("Hot Box updated")
            else:
                self.add_to_log(f"Error updating Hot Box: {result.message}")
                
        except Exception as e:
            logger.error(f"Error updating Hot Box: {e}")
            messagebox.showerror("Error", f"Could not update Hot Box: {e}")
    
    def setup_match_controls(self):
        """Set up the match control panel"""
        control_frame = ttk.Frame(self.master, padding="10")
        control_frame.grid(row=1, column=0, columnspan=3, sticky="ew")

        ttk.Button(control_frame, text="Pre-Match Roll", command=self.pre_match_roll).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Post-Match Roll", command=self.post_match_roll).pack(side="left", padx=5)

        ttk.Label(control_frame, text="Set Position:").pack(side="left", padx=5)
        ttk.Entry(control_frame, textvariable=self.position_var, width=5).pack(side="left")
        ttk.Button(control_frame, text="Set Favored", command=lambda: self.set_position("Favored")).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Set Underdog", command=lambda: self.set_position("Underdog")).pack(side="left", padx=5)

        ttk.Label(control_frame, text="In Control:").pack(side="left", padx=5)
        ttk.Combobox(control_frame, textvariable=self.in_control_var, values=["Favored", "Underdog", "Neither"]).pack(side="left")
        ttk.Button(control_frame, text="Set Control", command=self.set_in_control).pack(side="left", padx=5)

    def set_position(self, wrestler_type):
        """Set a wrestler's position on the board"""
        try:
            position = int(self.position_var.get())
            if 0 <= position <= 15:
                if wrestler_type == "Favored":
                    wrestler = self.game.favored_wrestler
                else:
                    wrestler = self.game.underdog_wrestler
                    
                if wrestler:
                    result = self.game.set_wrestler_position(wrestler, position)
                    if result.success:
                        self.update_display()
                        self.add_to_log(f"{wrestler_type} wrestler position set to {position}")
                    else:
                        self.add_to_log(f"Error: {result.message}")
                else:
                    messagebox.showerror("Error", f"No {wrestler_type.lower()} wrestler selected")
            else:
                messagebox.showerror("Error", "Position must be between 0 and 15")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the position")
        except Exception as e:
            logger.error(f"Error setting position: {e}")
            messagebox.showerror("Error", f"Could not set position: {e}")

    def setup_grade_update_controls(self):
        """Set up controls for updating wrestler grades"""
        update_frame = ttk.Frame(self.master, padding="10")
        update_frame.grid(row=3, column=0, columnspan=3, sticky="ew")

        ttk.Label(update_frame, text="Update Grade:").grid(row=0, column=0, sticky="w")
        self.update_wrestler_dropdown = ttk.Combobox(update_frame, textvariable=self.update_wrestler_var)
        self.update_wrestler_dropdown.grid(row=0, column=1, sticky="ew")

        ttk.Radiobutton(update_frame, text="Grudge", variable=self.grade_type_var, value="GRUDGE").grid(row=0, column=2)
        ttk.Radiobutton(update_frame, text="TV", variable=self.grade_type_var, value="TV").grid(row=0, column=3)

        ttk.Entry(update_frame, textvariable=self.new_grade_var, width=5).grid(row=0, column=4)
        ttk.Button(update_frame, text="Update Grade", command=self.update_grade).grid(row=0, column=5, padx=5)

    def setup_gui(self):
        """Set up the main GUI layout"""
        self.master.title("Face to the Mat")
        self.master.geometry("825x725")
        self.master.minsize(825, 725)  # Set minimum size
        self.master.maxsize(825, 725)  # Set maximum size (same as initial size)

        # Main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Left column: Wrestler selection and info
        left_frame = ttk.Frame(main_frame, padding="5")
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(left_frame, text="Favored Wrestler:").grid(row=0, column=0, sticky=tk.W)
        self.favored_dropdown = ttk.Combobox(left_frame, textvariable=self.favored_var)
        self.favored_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.favored_dropdown.bind("<<ComboboxSelected>>", self.update_favored_wrestler)

        ttk.Label(left_frame, text="Underdog Wrestler:").grid(row=1, column=0, sticky=tk.W)
        self.underdog_dropdown = ttk.Combobox(left_frame, textvariable=self.underdog_var)
        self.underdog_dropdown.grid(row=1, column=1, sticky=(tk.W, tk.E))
        self.underdog_dropdown.bind("<<ComboboxSelected>>", self.update_underdog_wrestler)

        self.wrestler_info = ttk.Label(left_frame, text="", justify=tk.LEFT)
        self.wrestler_info.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.N))

        # Middle column: Game controls and card info
        middle_frame = ttk.Frame(main_frame, padding="5")
        middle_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.action_button = ttk.Button(middle_frame, text="PLAY TURN", command=self.play_turn)
        self.action_button.pack(pady=(0, 10))

        self.card_frame = ttk.LabelFrame(middle_frame, text="Current Card", padding="5")
        self.card_frame.pack(fill=tk.X, expand=True)
        self.card_label = ttk.Label(self.card_frame, text="No card drawn yet", wraplength=300)
        self.card_label.pack()

        # Log frame
        self.log_frame = ttk.LabelFrame(middle_frame, text="Game Log", padding="5")
        self.log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.log_text = scrolledtext.ScrolledText(self.log_frame, wrap=tk.WORD, width=40, height=15)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)  # Make it read-only

        # Clear log button
        self.clear_log_button = ttk.Button(middle_frame, text="Clear Log", command=self.clear_log)
        self.clear_log_button.pack(pady=(10, 0))

        # Right column: Game board
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.board_canvas = tk.Canvas(right_frame, width=100, height=400)
        self.board_canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize the display
        self.update_display()

    def show_match_end_dialog(self, result):
        """Show dialog for match end"""
        end_dialog = tk.Toplevel(self.master)
        end_dialog.title("Match Result")
        
        message = tk.Label(end_dialog, text=result, padx=20, pady=20)
        message.pack()
        
        ok_button = ttk.Button(end_dialog, text="OK", command=end_dialog.destroy)
        ok_button.pack(pady=10)

    def update_board(self):
        """Update the game board visualization"""
        self.board_canvas.delete("all")
        space_height = 25
        space_width = 25
        
        # Draw board spaces
        for i in range(16):
            y = i * space_height
            if i in [5, 7, 9, 11, 12, 13, 14]:  # Square spaces
                self.board_canvas.create_rectangle(2, 2+y, space_width, y+space_height, fill="lightblue")
                # Add "PIN" text for PIN spaces
                if i >= 12:
                    self.board_canvas.create_text(space_width/2, y+space_height/2, text="PIN")
            else:  # Circle spaces
                self.board_canvas.create_oval(2, 2+y, space_width, y+space_height, fill="lightgreen")
            
            # Add space number
            self.board_canvas.create_text(space_width + 10, y+space_height/2, text=str(i))
            
            # Add "FINISHER" text for finisher space
            if i == 15:
                self.board_canvas.create_text(space_width/2, y+space_height/2, text="FIN")

        # Draw wrestler pieces
        piece_size = 15
        if self.game.favored_wrestler:
            favored_y = self.game.favored_wrestler.position * space_height + space_height/2
            self.board_canvas.create_oval(5, favored_y-piece_size/2, 5+piece_size, favored_y+piece_size/2, fill="blue")
        if self.game.underdog_wrestler:
            underdog_y = self.game.underdog_wrestler.position * space_height + space_height/2
            self.board_canvas.create_oval(space_width-5-piece_size, underdog_y-piece_size/2, space_width-5, underdog_y+piece_size/2, fill="red")

    def update_card_display(self, card_data=None):
        """Update the card display"""
        if not card_data:
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
        else:
            # Update from event data
            card_text = f"Move Type: {card_data['card_type']}\n"
            if isinstance(card_data['points'], dict):
                card_text += "Points: Varies by TV Grade\n"
            else:
                card_text += f"Points: {card_data['points']}\n"
            card_text += f"In-Control: {'Yes' if card_data['control'] else 'No'}"
            if 'text' in card_data and card_data['text']:
                card_text += f"\nText: {card_data['text']}"
            self.card_label.config(text=card_text)

    def update_display(self):
        """Update all display elements"""
        self.update_wrestler_info()
        self.update_board()
        self.update_card_display()
        self.update_in_control_display()
        self.update_hot_box_display()

    def update_grade(self):
        """Update a wrestler's grade"""
        try:
            wrestler_name = self.update_wrestler_var.get()
            if not wrestler_name:
                messagebox.showerror("Error", "Please select a wrestler.")
                return
                
            grade_type = self.grade_type_var.get()
            new_value = self.new_grade_var.get()
            
            result = self.game.update_wrestler_grade(wrestler_name, grade_type, new_value)
            if result.success:
                self.add_to_log(result.message)
                self.update_display()
                self.update_wrestler_dropdowns()
            else:
                self.add_to_log(f"Error: {result.message}")
        except Exception as e:
            logger.error(f"Error updating grade: {e}")
            messagebox.showerror("Error", f"Could not update grade: {e}")

    def update_hot_box_display(self):
        """Update the Hot Box display"""
        # Update dropdown visibility and content
        self.update_hot_box_dropdowns()

    def update_hot_box_dropdowns(self, event=None):
        """Update the Hot Box dropdown options"""
        try:
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
                if len(top_grudge_wrestlers) > 1:
                    self.grudge2_var.set(top_grudge_wrestlers[1].name)
        except Exception as e:
            logger.error(f"Error updating Hot Box dropdowns: {e}")
            # Don't show message box here as this might be called frequently

    def update_favored_wrestler(self, event):
        """Update the favored wrestler selection"""
        try:
            selected_name = self.favored_var.get()
            wrestler = self.game.wrestler_manager.get_wrestler(selected_name)
            if wrestler:
                result = self.game.setup_wrestlers(selected_name, self.underdog_var.get() or "")
                if result.success:
                    self.update_display()
                    self.update_hot_box_dropdowns()
                    logger.info(f"Favored wrestler set to {selected_name}")
                else:
                    self.add_to_log(f"Error: {result.message}")
        except Exception as e:
            logger.error(f"Error setting favored wrestler: {e}")
            messagebox.showerror("Error", f"Could not set favored wrestler: {e}")

    def update_in_control_display(self):
        """Update the in-control display"""
        if self.game.in_control == self.game.favored_wrestler:
            control_text = "Favored"
        elif self.game.in_control == self.game.underdog_wrestler:
            control_text = "Underdog"
        else:
            control_text = "Neither"
        self.in_control_var.set(control_text)

    def update_underdog_wrestler(self, event):
        """Update the underdog wrestler selection"""
        try:
            selected_name = self.underdog_var.get()
            wrestler = self.game.wrestler_manager.get_wrestler(selected_name)
            if wrestler:
                result = self.game.setup_wrestlers(self.favored_var.get() or "", selected_name)
                if result.success:
                    self.update_display()
                    self.update_hot_box_dropdowns()
                    logger.info(f"Underdog wrestler set to {selected_name}")
                else:
                    self.add_to_log(f"Error: {result.message}")
        except Exception as e:
            logger.error(f"Error setting underdog wrestler: {e}")
            messagebox.showerror("Error", f"Could not set underdog wrestler: {e}")

    def update_wrestler_dropdowns(self):
        """Update all wrestler dropdown options"""
        try:
            wrestler_names = sorted([w.name for w in self.game.wrestlers])
            if self.favored_dropdown:
                self.favored_dropdown['values'] = wrestler_names
            if self.underdog_dropdown:
                self.underdog_dropdown['values'] = wrestler_names
            self.update_hot_box_dropdowns()
            
            if self.update_wrestler_dropdown:
                self.update_wrestler_dropdown['values'] = wrestler_names
        except Exception as e:
            logger.error(f"Error updating wrestler dropdowns: {e}")
            messagebox.showerror("Error", f"Could not update wrestler dropdowns: {e}")

    def update_wrestler_info(self):
        """Update the wrestler info display"""
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
                    finisher_range = wrestler.finisher.get('range', (0, 0))
                    if isinstance(finisher_range, (list, tuple)) and len(finisher_range) >= 2:
                        range_str = f"{finisher_range[0]}-{finisher_range[1]}"
                    else:
                        range_str = str(finisher_range)
                    info_text += f"  Finisher: {wrestler.finisher['name']} (Range: {range_str})\n"
                info_text += "\n"
        self.wrestler_info.config(text=info_text)