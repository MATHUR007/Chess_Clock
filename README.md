# Chess_Clock
# Chess Puzzle Alarm Clock

Wake up your brain with chess puzzles! This application combines an alarm clock with chess puzzles that you need to solve in order to turn off the alarm.

## Features

- **Alarm Clock Functionality**: Set alarms for specific times with customizable difficulty levels.
- **Chess Puzzles**: Solve chess puzzles to turn off the alarm or practice anytime.
- **Difficulty Levels**: Choose between easy, medium, and hard puzzles.
- **Board Themes**: Change the appearance of the chess board with different color themes.
- **Custom Chess Board Renderer**: Built with Tkinter Canvas for a clean presentation.
- **Expandable Puzzle Database**: Includes default puzzles and can load additional puzzles from a local file.

#Chess Symbols
https://www.namecheap.com/visual/font-generator/chess-symbols/

## Requirements

- Python 3.x
- Required Python libraries:
  - tkinter (usually comes with Python)
  - python-chess

## Installation

1. Ensure you have Python installed on your system.
2. Install the required packages:
   ```bash
   pip install python-chess
   ```
3. Download the source code.
4. Run the application:
   ```bash
   python Chess_Clock.py
   ```

## Usage

### Setting an Alarm

1. Navigate to the "Alarm" tab.
2. Set the hour and minute for your alarm.
3. Select the puzzle difficulty you want to solve when the alarm triggers.
4. Click "Set Alarm".

### Solving Puzzles

1. When an alarm triggers, a chess puzzle will be displayed.
2. Enter your move in algebraic notation (e.g., "e2e4" or "Nf3").
3. Click "Submit Move".
4. If your move is correct, the alarm will stop. If not, try again!

### Practice Mode

1. Go to the "Puzzle" tab.
2. Click "Try a Random Puzzle" to practice without setting an alarm.

### Settings

Access the "Settings" tab to:
- Adjust the alarm volume
- Configure auto-increasing difficulty 
- Enable/disable snooze option with easier puzzles
- Change the board theme

## Adding Custom Puzzles

You can add custom puzzles by creating a file named `chess_puzzles.json` in the same directory as the application. The file should contain an array of puzzle objects with the following format:

```json
[
  {
    "fen": "chess position in FEN notation",
    "description": "Puzzle description",
    "solution": "expected move in UCI format (e.g., 'e2e4')",
    "difficulty": "easy|medium|hard"
  }
]
```

## About Chess Notation

The application supports multiple chess notation formats:
- UCI notation (e.g., "e2e4")
- Capture notation (e.g., "e2xe4")
- Standard Algebraic Notation (SAN) (e.g., "Nf3")

## Technical Details

- Built using Tkinter for the GUI
- Uses the python-chess library for chess logic
- Chess pieces are rendered using Unicode symbols
- Multi-threaded design to monitor alarms and play sounds
- Board positions are represented using FEN (Forsyth-Edwards Notation)

