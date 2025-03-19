# Face to the Mat - GUI Update Plan

## Overview
The current GUI (`game_gui.py`) needs to be updated to work with our refactored game logic. The changes should maintain the same visual appearance and user experience while connecting to the new, more modular backend code.

## Goals

1. Maintain existing UI appearance and functionality
2. Connect to refactored game logic and managers
3. Implement better error handling and user feedback
4. Improve Hot Box implementation
5. Add proper documentation

## Update Approach
### Phase 1: Basic Integration
1. **Update imports**
   - Import from refactored modules: `card_manager`, `wrestler_manager`, `game_utilities`
   - Replace direct references to game components
2. **Refactor event handlers**
   - Update all methods that interact with the game logic
   - Add error handling to all event handlers
3. **Implement logging**
   - Use the logger from `game_utilities` for all log messages
   - Add appropriate log messages for key events

### Phase 2: Enhanced Features
1. **Improve Hot Box UI**
   - Create better visualization of wrestler relationships
   - Add UI for managing allies and foes
   - Implement automatic grudge wrestler selection
2. **Add match history view**
   - Create a panel or window for viewing past matches
   - Display match statistics and outcomes
3. **Enhance board visualization**
   - Improve the game board representation
   - Add better visual cues for space types
   - Enhance wrestler position display

### Phase 3: Visual Improvements
1. **Update styles and themes**
   - Implement a consistent color scheme
   - Add proper spacing and padding
   - Improve control layouts
2. **Add tooltips and help**
   - Provide contextual help for game elements
   - Display card information in tooltips
   - Add better feedback for user actions

## Implementation Details

### GameGUI Class Updates

```python
class GameGUI:
    """
    Graphical User Interface for the Face to the Mat game.
    
    This class handles the display and user interaction for the wrestling game,
    connecting to the game logic to update the display and process user actions.
    
    Attributes:
        master (tk.Tk): The main Tkinter window
        game (Game): The game logic instance
        [other UI elements]
    """
    
    def __init__(self, master, game):
        self.master = master
        self.game = game
        
        # Initialize variables for dropdowns
        self.favored_var = tk.StringVar()
        self.underdog_var = tk.StringVar()
        self.favored_ally_var = tk.StringVar()
        self.favored_foe_var = tk.StringVar()
        self.underdog_ally_var = tk.StringVar()
        self.underdog_foe_var = tk.StringVar()
        self.grudge1_var = tk.StringVar()
        self.grudge2_var = tk.StringVar()
        self.in_control_var = tk.StringVar(value="Neither")
        
        # Initialize UI components
        self.setup_gui()
        self.setup_match_controls()
        self.setup_hot_box()
        self.setup_grade_update_controls()
        self.update_wrestler_dropdowns()
```

### Key Method Updates
1. **Update Wrestler Selection**
   ```python
   def update_favored_wrestler(self, event):
       selected_name = self.favored_var.get()
       wrestler = self.game.wrestler_manager.get_wrestler(selected_name)
       if wrestler:
           self.game.favored_wrestler = wrestler
           self.update_display()
           self.update_hot_box_dropdowns()
   ```

2. **Play Turn**
   ```python
   def play_turn(self):
       if not self.game.favored_wrestler or not self.game.underdog_wrestler:
           self.add_to_log("Please select wrestlers to begin the game.")
           return
           
       try:
           result = self.game.play_turn()
           self.add_to_log(result)
           self.update_display()
           self.update_in_control_display()
       except Exception as e:
           logger.error(f"Error playing turn: {e}")
           self.add_to_log(f"Error occurred: {e}")
   ```

3. **Update Hot Box**
   ```python
   def update_hot_box(self):
       # Set up Hot Box in the game logic
       self.game.setup_hot_box(
           favored_ally_name=self.favored_ally_var.get() or None,
           favored_foe_name=self.favored_foe_var.get() or None,
           underdog_ally_name=self.underdog_ally_var.get() or None,
           underdog_foe_name=self.underdog_foe_var.get() or None
       )
       
       # Update the UI to reflect changes
       self.update_hot_box_display()
   ```

## Testing Plan
1. **Unit Tests**
   - Create unit tests for GameGUI components
   - Test each UI interaction separately
2. **Integration Tests**
   - Test the UI with the refactored game logic
   - Ensure all actions properly update the game state
3. **User Acceptance Testing**
   - Have users test the updated UI
   - Collect feedback on usability and visual design

## Timeline
1. **Phase 1: Basic Integration** - 1-2 days
2. **Phase 2: Enhanced Features** - 3-5 days
3. **Phase 3: Visual Improvements** - 2-3 days

Total estimated time: 6-10 days

## Future Considerations
- Consider migrating to a more modern UI framework in the future
- Add support for themes and user customization
- Implement animation for card draws and wrestler movements
- Add sound effects for key game events
- Create a better visualization for submission and finisher moves