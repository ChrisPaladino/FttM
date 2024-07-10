import tkinter as tk
from tkinter import ttk

class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.setup_gui()

    def setup_gui(self):
        self.master.title("Face to the Mat")
        self.frame = ttk.Frame(self.master, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Wrestler info
        self.favored_label = ttk.Label(self.frame, text="")
        self.favored_label.grid(row=0, column=0)
        self.underdog_label = ttk.Label(self.frame, text="")
        self.underdog_label.grid(row=0, column=1)

        # Game board
        self.board_canvas = tk.Canvas(self.frame, width=400, height=200)
        self.board_canvas.grid(row=1, column=0, columnspan=2)

        # Card display
        self.card_canvas = tk.Canvas(self.frame, width=100, height=150)
        self.card_canvas.grid(row=2, column=0)

        # Action button
        self.action_button = ttk.Button(self.frame, text="Play Turn", command=self.play_turn)
        self.action_button.grid(row=2, column=1)

        # Result display
        self.result_label = ttk.Label(self.frame, text="", wraplength=300)
        self.result_label.grid(row=3, column=0, columnspan=2)

        self.update_display()

    def play_turn(self):
        result, card = self.game.play_turn()
        self.result_label.config(text=result)
        self.update_display()
        self.draw_card(card)
        
        if self.game.check_win_condition():
            self.action_button.config(state="disabled")
            winner = self.game.favored_wrestler if self.game.favored_wrestler.position >= 15 else self.game.underdog_wrestler
            self.result_label.config(text=f"Game Over! {winner.name} wins!")

    def update_display(self):
        favored = self.game.favored_wrestler
        underdog = self.game.underdog_wrestler
        
        self.favored_label.config(text=f"{favored.name}\nPosition: {favored.position}")
        self.underdog_label.config(text=f"{underdog.name}\nPosition: {underdog.position}")

        # Update board
        self.board_canvas.delete("all")
        self.draw_board()
        self.draw_wrestlers()

    def draw_board(self):
        for i in range(16):
            x = i * 25
            y = 100
            if i in [5, 7, 9, 11, 12, 13, 14]:  # Square spaces
                self.board_canvas.create_rectangle(x, y-10, x+20, y+10, fill="lightblue")
            else:  # Circle spaces
                self.board_canvas.create_oval(x, y-10, x+20, y+10, fill="lightgreen")
            if i >= 12:  # PIN spaces
                self.board_canvas.create_text(x+10, y+20, text="PIN")

    def draw_card(self, card):
        if card:
            self.card_canvas.delete("all")
            self.card_canvas.create_rectangle(10, 10, 90, 140, fill="white", outline="black")
            self.card_canvas.create_text(50, 30, text=card.move_type, font=("Arial", 10, "bold"))
            self.card_canvas.create_text(50, 70, text=f"Points: {card.points}", font=("Arial", 10))
            moves_text = "\n".join(card.specific_moves[:3])  # Show first 3 moves
            self.card_canvas.create_text(50, 110, text=moves_text, font=("Arial", 8), width=70)

    def draw_wrestlers(self):
        favored_x = self.game.favored_wrestler.position * 25
        underdog_x = self.game.underdog_wrestler.position * 25
        self.board_canvas.create_oval(favored_x, 80, favored_x+20, 100, fill="red")
        self.board_canvas.create_oval(underdog_x, 100, underdog_x+20, 120, fill="blue")