import tkinter as tk
import os
import sys
import logging
from typing import Optional

# Add project root to path for imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.game_logic import Game
from src.game_gui import GameGUI
from src.game_utilities import logger

def main():
    # Set up logging
    logger.info("Starting Face to the Mat application")
    
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Face to the Mat - Professional Wrestling Simulation")
    root.geometry("825x725")  # Default window size
    
    # Set application icon if available
    icon_path = os.path.join(project_root, 'data', 'icons', 'app_icon.png')
    if os.path.exists(icon_path):
        try:
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
        except Exception as e:
            logger.warning(f"Could not load application icon: {e}")
    
    # Initialize game logic
    try:
        game = Game()
        game.setup_game()
        logger.info("Game initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing game: {e}")
        error_window = tk.Toplevel(root)
        error_window.title("Initialization Error")
        tk.Label(error_window, text=f"Error initializing game: {e}", padx=20, pady=20).pack()
        tk.Button(error_window, text="OK", command=error_window.destroy).pack(pady=10)
        return
    
    # Initialize GUI with the game
    try:
        gui = GameGUI(root, game)
        logger.info("GUI initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing GUI: {e}")
        error_window = tk.Toplevel(root)
        error_window.title("GUI Error")
        tk.Label(error_window, text=f"Error initializing GUI: {e}", padx=20, pady=20).pack()
        tk.Button(error_window, text="OK", command=error_window.destroy).pack(pady=10)
        return
    
    # Set up application closing handler
    def on_closing():
        logger.info("Application closing")
        # Perform any cleanup needed here
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the Tkinter event loop
    try:
        logger.info("Starting main event loop")
        root.mainloop()
    except Exception as e:
        logger.error(f"Error in main event loop: {e}")
    finally:
        logger.info("Application terminated")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.critical(f"Unhandled exception in main: {e}")
        # Display a simple error message if the GUI hasn't initialized yet
        try:
            error_root = tk.Tk()
            error_root.title("Face to the Mat - Error")
            tk.Label(error_root, text=f"An unhandled error occurred: {e}", padx=20, pady=20).pack()
            tk.Button(error_root, text="OK", command=error_root.destroy).pack(pady=10)
            error_root.mainloop()
        except:
            # If even that fails, just print to console
            print(f"Critical error: {e}")