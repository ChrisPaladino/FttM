# Face to the Mat

A professional wrestling simulation game implemented in Python with a Tkinter GUI.

## Overview

Face to the Mat is a tabletop wrestling game that simulates professional wrestling matches and storylines. This digital implementation allows you to manage wrestlers, conduct matches, and build storylines using the game's mechanics.

## Features

- **Wrestler Management**: Create, edit, and manage wrestlers with detailed attributes
- **Match Simulation**: Conduct matches between wrestlers with different skills and abilities
- **Card-Based Action System**: Use Fast Action Cards (FACs) to determine match flow and outcomes
- **TV and Grudge Grades**: Track wrestler popularity and rivalries
- **Hot Box System**: Include allies and rivals to influence match outcomes
- **Specialty and Finisher Moves**: Wrestlers have unique signature moves and finishers

## Installation

1. Clone this repository
2. Ensure you have Python 3.6+ installed
3. Install required dependencies: `pip install tkinter`
4. Run the game: `python src/main.py`

## Project Structure

/FTTM
    /data
        /gamedata
            fac_deck.json       # The action card deck used to resolve moves
        /wrestlers
            /img                # Folder for wrestler images
            wrestlers.json      # Current wrestler data with stats and attributes
    /src
        game_gui.py            # The GUI implementation using Tkinter
        game_logic.py          # Core game mechanics and logic
        main.py                # Entry point for running the application
        new_wrestler_creation.py  # Script for creating new wrestlers
        wrestler_editor.py      # GUI for editing wrestler attributes
    README.md                  # This file
    Rulebook_v3.pdf            # Comprehensive game rules

## Game Components

### Wrestlers

Each wrestler has the following attributes:

- **Name, Sex, Height, Weight, Hometown**: Basic biographical information
- **TV Grade**: Popularity rating from AAA (highest) to F (lowest)
- **Grudge Grade**: Numerical value indicating rivalry intensity
- **Skills/Qualities**: 12 abilities including Agile, Strong, Smart, etc.
- **Specialty Move**: A signature move with point value
- **Finisher**: Ultimate move that can end a match

### Skills System

Skills are categorized by their availability:

- **Star**: Can be used at any time
- **Square**: Can only be used on square spaces (5, 7, 9, 11, 12, 13, 14)
- **Circle**: Can only be used on circle spaces (0, 1, 2, 3, 4, 6, 8, 10)

### Fast Action Cards (FACs)

Cards that determine match flow, with types including:

- Skill-specific (Agile, Strong, etc.)
- TV Move (based on TV Grade)
- Grudge (based on Grudge Grade)
- Wild Card (special events)
- Highlight Reel (storyline development)
- Special themed cards (Ref Bump, Test of Strength, etc.)

### Game Board

The match progression board has 16 spaces (0-15):

- Spaces 0-11: Regular moves
- Spaces 12-14: PIN attempt zones
- Space 15: FINISHER zone

## Game Flow

1. **Setup**: Select favored and underdog wrestlers, fill the Hot Box
2. **Pre-Match**: Optional storyline development
3. **Match**: Draw FACs to determine moves and points, advancing wrestlers on the track
4. **Resolution**: Match ends with successful pin, submission, or finisher
5. **Post-Match**: Optional storyline development

## Match Mechanics

- **Scoring**: Different card types award different point values
- **Skills**: Determine which wrestler can use a particular move
- **Tiebreakers**: Typically favor the trailing wrestler or the favored wrestler
- **Pins**: Defender must roll within their TV Grade range to kick out
- **Finishers**: Need to roll within the finisher's range to succeed

## Special Match Types

The game supports various match types:

- Grudge Matches
- Cage Matches
- Tag Team Matches
- Three-For-Alls
- Battle Royales
- Hardcore Matches

## Current Development Status

### Implemented Features

- Basic match simulation
- Wrestler management and editing
- Core card mechanics
- Match progression tracking
- Pin and finisher attempts

### Features In Progress

- Hot Box implementation: Ally and Foe mechanics
- Highlight Reel cards and Wild Card events
- Submission mechanics
- Pre and Post match charts
- TV Grade and Grudge Grade update system

### Future Enhancements

- Full implementation of all match types
- Enhanced visualization of the game board
- Tournament and federation management
- Wrestler ranking and pointing system
- Contracts and retirement system

## Contributing

Contributions are welcome! Please check the issues list or create a new issue to discuss proposed changes.

## License

[Your License Information Here]

#### Code Directory Structure

/FTTM
    /data
        /gamedata
            fac_deck.json (The action card deck used to resolve moves)
        /wrestlers
            /img (the folder where all images of wrestlers will reside)
            orig_wrestlers.json (the source / original wrestlers json)
            wrestlers.json (wrestlers in their current state, as they grow or lose experience, and wins and losses)
    /src
        game_gui.py
        game_logic.py
        main.py
        new wrestler creation.py
        wrestler_editor.py

---

#### GCW Women's tourney

- https://brackethq.com/b/x5n6b/

#### Implement

- Show full card text in the log.
- Only show changes in IN CONTROL wrestler
- Hot Box:
    - Grudge doesn't update if the wrestler is involved in the match
    - Need to implement ALLY and FOE in the Wrestler JSON
    - Need a way to do pre-match tweaks (TV Grade, Grudge Grade), and maybe Mid-Match as well?
- Explain how Signature is resolved?
    - We may need to have In-Control only for the 1 previous FAC, not a running total.
    - An alternative is that the Signature gives more points to whoever was in control
- Helped doesnt resolve properly if there's text and no points...
      {
        "id": 39,
        "control": false,
        "type": "Helped",
        "text": "Go to HIGHLIGHT REEL \"G\", \"M\" or \"V\" depending on the source of help."
      },
      {
        "id": 40,
        "control": false,
        "type": "Helped",
        "text": "Go to HIGHLIGHT REEL \"G\", \"M\" or \"V\" depending on the source of help."
      },
- Submission cards: moves break on 1-3 (1-4 if STRONG)
    - Confirm Submission works - why are we getting TV Grade?
- Editor needs images
- Wild Card / Highlight reel cards
    - Need to distinguish which skills are mental vs. physical
- Test of Strength cards: results (if both STRONG and/or POWERFUL)
     - 1-2: Face scores 1 point
     - 3-4: Ref breaks hold
     - 5-6: Heel scores 1 point

    - Verify this works, our underdog is STRONG: Star, so I suspect she CAN use the card
        Card drawn: Test of Strength (No Control)
        Card type: Test of Strength
        Favored can use: False
        Underdog can use: False
        Neither wrestler can use this skill. No points scored.
- HELP that makes you roll on the TYPE chart
    - G = gang/group
    - M = manager
    - V = valet
- Digitize the various charts
- Implement the Pre and Post match charts
- Ranking and pointing of wrestlers
     - https://www.reddit.com/r/FaceToTheMat/comments/noje6j/homebrew_fttm_overall_rating_based_on_attributes/
- Contracts
     - https://www.reddit.com/r/FaceToTheMat/comments/nm9hk7/houserules_face_to_the_mat_wrestler_contracts/
- Age / Retirement
