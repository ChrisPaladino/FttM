import tkinter as tk
from tkinter import ttk

class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.setup_gui()

    def setup_gui(self):
        self.master.title("Face to the Mat")
        self.master.geometry("1200x900")  # Increased height to accommodate card display

        # Wrestler info frames
        self.favored_frame = ttk.LabelFrame(self.master, text="Favored Wrestler", padding="10")
        self.favored_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.underdog_frame = ttk.LabelFrame(self.master, text="Underdog Wrestler", padding="10")
        self.underdog_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Game board
        self.board_canvas = tk.Canvas(self.master, width=800, height=200)
        self.board_canvas.grid(row=1, column=0, columnspan=2, pady=10)

        # Card display
        self.card_frame = ttk.LabelFrame(self.master, text="Current Card", padding="10")
        self.card_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.card_label = ttk.Label(self.card_frame, text="No card drawn yet")
        self.card_label.pack()

        # Action button
        self.action_button = ttk.Button(self.master, text="Play Turn", command=self.play_turn)
        self.action_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Result display
        self.result_label = ttk.Label(self.master, text="", wraplength=780)
        self.result_label.grid(row=4, column=0, columnspan=2, pady=10)

        self.update_display()

    def update_card_display(self):
        if self.game.current_card:
            card = self.game.current_card
            card_text = f"Move Type: {card.move_type}\n"
            card_text += f"Points: {card.points}\n"
            card_text += f"Specific Moves: {', '.join(card.specific_moves)}"
            self.card_label.config(text=card_text)
        else:
            self.card_label.config(text="No card drawn yet")

    def update_display(self):
        self.update_wrestler_info(self.favored_frame, self.game.favored_wrestler)
        self.update_wrestler_info(self.underdog_frame, self.game.underdog_wrestler)
        self.update_board()
        self.update_card_display()

    def update_wrestler_info(self, frame, wrestler):
        for widget in frame.winfo_children():
            widget.destroy()

        ttk.Label(frame, text=f"Name: {wrestler.name}").grid(row=0, column=0, sticky="w")
        ttk.Label(frame, text=f"Sex: {wrestler.sex}").grid(row=1, column=0, sticky="w")
        ttk.Label(frame, text=f"Height: {wrestler.height}").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text=f"Weight: {wrestler.weight}").grid(row=3, column=0, sticky="w")
        ttk.Label(frame, text=f"Hometown: {wrestler.hometown}").grid(row=4, column=0, sticky="w")
        ttk.Label(frame, text=f"TV Grade: {wrestler.tv_grade}").grid(row=5, column=0, sticky="w")
        ttk.Label(frame, text=f"Grudge Grade: {wrestler.grudge_grade}").grid(row=6, column=0, sticky="w")
        ttk.Label(frame, text=f"Position: {wrestler.position}").grid(row=7, column=0, sticky="w")

        ttk.Label(frame, text="Skills:").grid(row=8, column=0, sticky="w")
        for i, (skill, skill_type) in enumerate(wrestler.skills.items(), start=9):
            ttk.Label(frame, text=f"  {skill}: {skill_type}").grid(row=i, column=0, sticky="w")

        ttk.Label(frame, text=f"Specialty: {wrestler.specialty['name']} ({wrestler.specialty['points']})").grid(row=i+1, column=0, sticky="w")
        ttk.Label(frame, text=f"Finisher: {wrestler.finisher['name']} ({wrestler.finisher['range']})").grid(row=i+2, column=0, sticky="w")

    def update_board(self):
        self.board_canvas.delete("all")
        for i in range(16):
            x = i * 50
            y = 100
            if i in [5, 7, 9, 11, 12, 13, 14]:  # Square spaces
                self.board_canvas.create_rectangle(x, y-20, x+40, y+20, fill="lightblue")
            else:  # Circle spaces
                self.board_canvas.create_oval(x, y-20, x+40, y+20, fill="lightgreen")
            if i >= 12:  # PIN spaces
                self.board_canvas.create_text(x+20, y+30, text="PIN")

        favored_x = self.game.favored_wrestler.position * 50
        underdog_x = self.game.underdog_wrestler.position * 50
        self.board_canvas.create_oval(favored_x, 60, favored_x+40, 100, fill="red")
        self.board_canvas.create_oval(underdog_x, 100, underdog_x+40, 140, fill="blue")

    def play_turn(self):
        result = self.game.play_turn()
        self.result_label.config(text=result)
        self.update_display()
        
        if self.game.check_win_condition():
            self.action_button.config(state="disabled")
            winner = self.game.favored_wrestler if self.game.favored_wrestler.position >= 15 else self.game.underdog_wrestler
            self.result_label.config(text=f"Game Over! {winner.name} wins!")