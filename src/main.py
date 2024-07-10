import tkinter as tk
from game_logic import Game
from game_gui import GameGUI

def main():
    root = tk.Tk()
    game = Game()
    game.setup_game()
    
    gui = GameGUI(root, game)
    root.mainloop()

if __name__ == "__main__":
    main()