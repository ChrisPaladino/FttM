1. In game_gui.py's update_board function:
    a. I changed the wrestler piece colors: favorite is blue, underdog is red
    b. I changed the sizes of the spaces to ensure the circles and squares are not ovals and rectangles
2. In game_logic.py, does the wrestler's is_trailing look at the underdog if the positions are tied?
3. I got a recursive error:
    File "c:\GitHub\FttM\src\game_logic.py", line 131, in resolve_in_control_card
        return "No wrestler in control. Treating as a normal card. \n" + self.resolve_card(card)
                                                                        ^^^^^^^^^^^^^^^^^^^^^^^
    RecursionError: maximum recursion depth exceeded
4. I'd like you to update the manual to better handle the rules we discussed around how to resolve a FAC
    a. Check if either or both wrestlers have the skill. If neither, draw a new FAC. If both, resolve tiebreaker
        i. Tiebreaker = whichever wrestler is trailing wins the points. If the wrestlers are on the same position, then the underdog score the points
    b. In-control gives the wrestler who score on the previous FAC (if any) a free check to see if they have the skill on the In-Control FAC. If so, they win the points, otherwise, draw a new card, and check only the other (non-scoring on the last FAC) wrestler to see if they have the skill. If neither do, reset the last_scorer (since neither scored), and continue drawing FACs
5. Need to implement cards: TV Grade, Grudge, Submission, Specialty, Signature (similar to an In-Control)
6. If the points is a d6, then show the amount of points rolled.