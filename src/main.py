import tkinter as tk
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.game_logic import Game
from src.game_gui import GameGUI

def main():
    root = tk.Tk()
    game = Game()
    game.setup_game()
    
    gui = GameGUI(root, game)
    root.mainloop()

if __name__ == "__main__":
    main()