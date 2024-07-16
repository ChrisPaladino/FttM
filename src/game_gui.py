import tkinter as tk
from tkinter import ttk

class GameGUI:
    def __init__(self, master, game):
        self.master = master
        self.game = game
        self.setup_gui()

    def play_turn(self):
        if not self.game.favored_wrestler or not self.game.underdog_wrestler:
            self.result_label.config(text="Please select wrestlers to begin the game.")
            return
        result = self.game.play_turn()
        self.result_label.config(text=result)
        self.update_display()
        
        if self.game.check_win_condition():
            self.action_button.config(state="disabled")

    def setup_gui(self):
        self.master.title("Face to the Mat")
        self.master.geometry("1000x600")

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
        self.favored_var = tk.StringVar()
        self.favored_dropdown = ttk.Combobox(left_frame, textvariable=self.favored_var)
        self.favored_dropdown.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.favored_dropdown.bind("<<ComboboxSelected>>", self.update_favored_wrestler)

        ttk.Label(left_frame, text="Underdog Wrestler:").grid(row=1, column=0, sticky=tk.W)
        self.underdog_var = tk.StringVar()
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
        self.card_label = ttk.Label(self.card_frame, text="No card drawn yet")
        self.card_label.pack()

        self.result_label = ttk.Label(middle_frame, text="", wraplength=200)
        self.result_label.pack(pady=5)

        # Right column: Game board
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.grid(row=0, column=2, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.board_canvas = tk.Canvas(right_frame, width=100, height=400)
        self.board_canvas.pack(fill=tk.BOTH, expand=True)

        self.update_wrestler_dropdowns()
        self.update_display()

    def update_board(self):
        self.board_canvas.delete("all")
        space_height = 25
        space_width = 25
        for i in range(16):
            y = i * space_height
            if i in [5, 7, 9, 11, 12, 13, 14]:  # Square spaces
                self.board_canvas.create_rectangle(2, 2+y, space_width, y+space_height, fill="lightblue")
            else:  # Circle spaces
                self.board_canvas.create_oval(2, 2+y, space_width, y+space_height, fill="lightgreen")
            self.board_canvas.create_text(space_width + 10, y+space_height/2, text=str(i))
            if i >= 12:  # PIN spaces
                self.board_canvas.create_text(space_width/2, y+space_height/2, text="PIN")

        piece_size = 15
        if self.game.favored_wrestler:
            favored_y = self.game.favored_wrestler.position * space_height + space_height/2
            self.board_canvas.create_oval(5, favored_y-piece_size/2, 5+piece_size, favored_y+piece_size/2, fill="blue")
        if self.game.underdog_wrestler:
            underdog_y = self.game.underdog_wrestler.position * space_height + space_height/2
            self.board_canvas.create_oval(space_width-5-piece_size, underdog_y-piece_size/2, space_width-5, underdog_y+piece_size/2, fill="red")

    def update_card_display(self):
        if self.game.current_card:
            card = self.game.current_card
            card_text = f"Move Type: {card.type}\n"
            card_text += f"Points: {card.points}\n"
            card_text += f"In-Control: {'Yes' if card.control else 'No'}"
            self.card_label.config(text=card_text)
        else:
            self.card_label.config(text="No card drawn yet")

    def update_display(self):
        self.update_wrestler_info()
        self.update_board()
        self.update_card_display()

    def update_favored_wrestler(self, event):
        selected_name = self.favored_var.get()
        self.game.favored_wrestler = next(w for w in self.game.wrestlers if w.name == selected_name)
        self.update_display()

    def update_underdog_wrestler(self, event):
        selected_name = self.underdog_var.get()
        self.game.underdog_wrestler = next(w for w in self.game.wrestlers if w.name == selected_name)
        self.update_display()

    def update_wrestler_dropdowns(self):
        wrestler_names = [w.name for w in self.game.wrestlers]
        self.favored_dropdown['values'] = wrestler_names
        self.underdog_dropdown['values'] = wrestler_names

    def update_wrestler_info(self):
        info_text = ""
        if self.game.favored_wrestler:
            info_text += f"Favored: {self.game.favored_wrestler.name}\n"
            info_text += f"  Position: {self.game.favored_wrestler.position}\n"
            info_text += f"  TV Grade: {self.game.favored_wrestler.tv_grade}\n"
            info_text += f"  Grudge Grade: {self.game.favored_wrestler.grudge_grade}\n"
            info_text += f"  Skills: {', '.join(self.game.favored_wrestler.skills)}\n\n"
        if self.game.underdog_wrestler:
            info_text += f"Underdog: {self.game.underdog_wrestler.name}\n"
            info_text += f"  Position: {self.game.underdog_wrestler.position}\n"
            info_text += f"  TV Grade: {self.game.underdog_wrestler.tv_grade}\n"
            info_text += f"  Grudge Grade: {self.game.underdog_wrestler.grudge_grade}\n"
            info_text += f"  Skills: {', '.join(self.game.underdog_wrestler.skills)}\n"
        self.wrestler_info.config(text=info_text)