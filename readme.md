# 🥊 Face to the Mat

*A Python-based digital adaptation of the classic pro wrestling card game.*

## 🎮 Game Overview

**Face to the Mat** is a simulation-style wrestling game where players control wrestlers and experience dramatic matches and storylines through Fast Action Cards (FACs), dice rolls, and stat-based mechanics. This Python implementation brings the tabletop game to life — with match simulation, career tracking, and storyline progression.

## 🚀 Features

- 🧍 Wrestler creation, editing, and stat management
- 🃏 Card-based match resolution using a custom FAC deck
- 📺 Popularity and rivalry tracked via TV Grade and Grudge Grade
- 🎭 Match storytelling via Highlight Reels, Pre/Post match events
- 🤼‍♂️ Support for special match types: Grudge, Tag, Hardcore, etc.
- 🖥️ GUI support with optional Tkinter interface (in development)

## 🛠️ Installation

git clone <https://github.com/chrispaladino/face-to-the-mat.git>
cd face-to-the-mat
pip install -r requirements.txt
python src/main.py

> Python 3.7+ required. Tkinter should be pre-installed, but if not:
> `sudo apt install python3-tk` (Linux) or `brew install python-tk` (Mac)

## 🗂 Project Structure

FTTM/
├── data/
│   ├── gamedata/
│   │   └── fac_deck.json
│   └── wrestlers/
│       ├── orig_wrestlers.json
│       └── wrestlers.json
├── docs/
│   ├── Rulebook_v3.pdf
├── src/
│   ├── main.py
│   ├── game_logic.py
│   ├── game_gui.py
│   ├── card_manager.py
│   ├── wrestler_manager.py
│   ├── new_wrestler_creation.py
│   ├── wrestler_editor.py
│   └── game_utilities.py
└── README.md

## 🧩 Game Rules & Flow

See [Markdown Rulebook](./docs/Rulebook_v4.md) for full gameplay mechanics.

### 🛎️ Core Concepts

- **Match Track**: 0–15 spaces, used to determine match progression
- **FAC Types**: Skill, TV Move, Grudge, Wild Card, Highlight Reel, Special
- **Skills**: 12 qualities each wrestler may have (AGILE, STRONG, etc.)
- **Symbols**: `★` Star (anytime), `■` Square (square spaces), `●` Circle (circle spaces)
- **Finishers**: Special roll-based moves that end matches if successful

## 🔁 Game Loop

1. **Setup** wrestlers and Hot Box (allies/foes)
2. **Pre-Match**: Optional Highlight Reel
3. **Draw FACs** → resolve actions, move tokens
4. **Check** for PIN or FINISHER
5. **Post-Match**: Optional story development

## 🧪 Current Implementation Status

### ✅ Completed

- [x] Basic 1v1 match simulation
- [x] Wrestler editor & data loader
- [x] TV Grade / Grudge Grade handling
- [x] Core FAC resolution & scoring
- [x] Pin & Finisher logic

### 🔧 In Progress

- [ ] Hot Box ally/foe logic
- [ ] Highlight Reel system
- [ ] Submission mechanics
- [ ] Wild Card & Special Event cards
- [ ] Mid-match stat changes

### 🧭 Roadmap

- [ ] Tag team transitions & hot tags
- [ ] Full match type support (Cage, Hardcore, etc.)
- [ ] Career tracking, aging, and contracts
- [ ] Wrestler rankings and federation management
- [ ] Federation-wide tournaments and story arcs

## 📝 Developer Notes

See [`docs/developmentroadmap.md`](./docs/developmentroadmap.md) for full backlog and rule integration status.

### Example: Remaining FAC Issues

{
  "id": 40,
  "type": "Helped",
  "text": "Go to HIGHLIGHT REEL 'G', 'M' or 'V' depending on the source of help."
}

- HELPED results may not trigger properly if no points are attached
- Highlight Reel routing system not fully digitized
- Need to distinguish mental vs. physical skills for certain cards

## 🏆 Community Resources

- GCW Women’s Tournament: <https://brackethq.com/b/x5n6b/>
- Wrestler Rating Homebrew: [Reddit post](https://www.reddit.com/r/FaceToTheMat/comments/noje6j/homebrew_fttm_overall_rating_based_on_attributes/)
- Wrestler Contracts: [Reddit house rules](https://www.reddit.com/r/FaceToTheMat/comments/nm9hk7/houserules_face_to_the_mat_wrestler_contracts/)
