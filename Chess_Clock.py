import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import time
import threading
import chess
import random
import json
import os

class ChessBoardCanvas(tk.Canvas):
    """Custom chess board renderer using Tkinter Canvas"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.square_size = 50
        self.board_size = self.square_size * 8
        self.config(width=self.board_size, height=self.board_size)
        
        # Colors
        self.light_color = "#F0D9B5"  # Light squares
        self.dark_color = "#B58863"   # Dark squares
        self.highlight_color = "#AAD955"  # Highlighted squares
        
        # Unicode chess piece symbols
        self.pieces = {
            'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',  # White pieces
            'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚',  # Black pieces
        }
        
        # Font for pieces
        self.piece_font = ("Arial", int(self.square_size * 0.7), "bold")
        
        # Initialize board
        self.board = chess.Board()
        self.draw_board()
    
    def draw_board(self):
        """Draw the chess board and pieces"""
        self.delete("all")  # Clear canvas
        
        # Draw board squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Alternate square colors
                color = self.light_color if (row + col) % 2 == 0 else self.dark_color
                self.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
                # Add coordinate labels
                if col == 0:  # Left edge - row numbers
                    self.create_text(
                        x1 + 5, 
                        y1 + self.square_size/2, 
                        text=str(8-row),
                        anchor="w",
                        font=("Arial", 10),
                        fill="#000000" if (row % 2 == 0) else "#FFFFFF"
                    )
                
                if row == 7:  # Bottom edge - column letters
                    self.create_text(
                        x1 + self.square_size/2, 
                        y2 - 5, 
                        text=chr(97 + col),  # 'a' through 'h'
                        anchor="s",
                        font=("Arial", 10),
                        fill="#000000" if ((row + col) % 2 == 0) else "#FFFFFF"
                    )
        
        # Draw pieces
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                # Calculate position
                col = chess.square_file(square)
                row = 7 - chess.square_rank(square)  # Flip because chess board has rank 8 at the top
                
                x = col * self.square_size + self.square_size / 2
                y = row * self.square_size + self.square_size / 2
                
                # Get piece symbol
                symbol = self.pieces[piece.symbol()]
                
                # Draw piece
                self.create_text(
                    x, y, 
                    text=symbol, 
                    font=self.piece_font,
                    fill="white" if piece.color == chess.BLACK else "black"
                )
    
    def update_board(self, board):
        """Update with a new board position"""
        self.board = board
        self.draw_board()

class ChessPuzzleAlarm:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Puzzle Alarm Clock")
        self.root.geometry("800x650")
        self.root.resizable(True, True)
        
        self.alarms = []
        self.current_alarm = None
        self.alarm_active = False
        self.alarm_thread = None
        self.puzzle_thread = None
        
        self.board = chess.Board()
        self.current_puzzle = None
        self.expected_move = None
        
        self.setup_ui()
        self.setup_puzzles()
        self.check_alarms_thread = threading.Thread(target=self.check_alarms, daemon=True)
        self.check_alarms_thread.start()
    
    def setup_puzzles(self):
        # Sample puzzles - in a real app, you'd have a larger database
        self.puzzles = [
            {
                "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
                "description": "Find the best move for White",
                "solution": "f3d5",  # Knight takes e5
                "difficulty": "easy"
            },
            {
                "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
                "description": "Find the fork",
                "solution": "f3g5",  # Knight to g5 fork
                "difficulty": "easy"
            },
            {
                "fen": "r1bqkb1r/pppp1Qpp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNB1K2R b KQkq - 0 1",
                "description": "Find the best defense",
                "solution": "d8f7",  # Queen takes queen
                "difficulty": "medium"
            },
            {
                "fen": "r3k2r/pp3ppp/2p5/4Pb2/2B2P2/8/PPP3PP/R3K2R w KQkq - 0 1",
                "description": "Mate in 1",
                "solution": "c4f7",  # Bishop checkmate
                "difficulty": "easy"
            },
            {
                "fen": "3r1rk1/pp3ppp/2p5/8/3P4/8/PPP2PPP/R3K2R w KQ - 0 1",
                "description": "Find the best move",
                "solution": "e1c1",  # Castle queenside
                "difficulty": "medium"
            },
            {
                "fen": "r1bq1rk1/pp2ppbp/2np1np1/8/2BNP3/2N1BP2/PPP3PP/R2QK2R w KQ - 0 1",
                "description": "Find the best move for White",
                "solution": "d4f5",  # Knight to f5
                "difficulty": "medium"
            },
            {
                "fen": "r4rk1/pp1n1ppp/2p1p3/q2p4/8/P1NPP1P1/1PPQ1PBP/R3K2R w KQ - 0 1",
                "description": "Find the best move for White",
                "solution": "d3d4",  # Opening the diagonal for the bishop
                "difficulty": "medium"
            },
            {
                "fen": "r1b1kb1r/pp3ppp/2n1pn2/q1pp4/3P4/P1N1PN2/1PP1BPPP/R1BQK2R w KQkq - 0 1",
                "description": "Find a strong developing move",
                "solution": "c1g5",  # Bishop to g5
                "difficulty": "medium"
            },
            {
                "fen": "r3kb1r/ppp2ppp/2n1b3/3q4/3pN3/8/PPP2PPP/RNBQR1K1 w kq - 0 1",
                "description": "Find the winning tactic",
                "solution": "e4d6",  # Knight fork
                "difficulty": "easy"
            },
            {
                "fen": "2r3k1/pp2ppbp/3p2p1/3P4/3b4/P4N2/1P3PPP/2B1R1K1 w - - 0 1",
                "description": "Find the best move for White",
                "solution": "c1h6",  # Bishop to h6
                "difficulty": "hard"
            }
        ]
        
        # Check if we have a local file with saved puzzles and load it
        if os.path.exists("chess_puzzles.json"):
            try:
                with open("chess_puzzles.json", "r") as f:
                    additional_puzzles = json.load(f)
                    self.puzzles.extend(additional_puzzles)
            except:
                pass
    
    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Alarm Tab
        alarm_tab = ttk.Frame(notebook)
        notebook.add(alarm_tab, text="Alarm")
        
        # Puzzle Tab
        puzzle_tab = ttk.Frame(notebook)
        notebook.add(puzzle_tab, text="Puzzle")
        
        # Settings Tab
        settings_tab = ttk.Frame(notebook)
        notebook.add(settings_tab, text="Settings")
        
        # Setup Alarm Tab
        self.setup_alarm_tab(alarm_tab)
        
        # Setup Puzzle Tab
        self.setup_puzzle_tab(puzzle_tab)
        
        # Setup Settings Tab
        self.setup_settings_tab(settings_tab)
    
    def setup_alarm_tab(self, parent):
        # Alarm setting frame
        set_frame = ttk.LabelFrame(parent, text="Set Alarm")
        set_frame.pack(fill="x", padx=10, pady=10)
        
        # Time selection
        time_frame = ttk.Frame(set_frame)
        time_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(time_frame, text="Hour:").pack(side="left", padx=5)
        self.hour_spinbox = ttk.Spinbox(time_frame, from_=0, to=23, width=3)
        self.hour_spinbox.pack(side="left", padx=5)
        
        ttk.Label(time_frame, text="Minute:").pack(side="left", padx=5)
        self.minute_spinbox = ttk.Spinbox(time_frame, from_=0, to=59, width=3)
        self.minute_spinbox.pack(side="left", padx=5)
        
        # Difficulty selection
        difficulty_frame = ttk.Frame(set_frame)
        difficulty_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(difficulty_frame, text="Puzzle Difficulty:").pack(side="left", padx=5)
        self.difficulty_var = tk.StringVar(value="easy")
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var)
        difficulty_combo['values'] = ('easy', 'medium', 'hard')
        difficulty_combo.pack(side="left", padx=5)
        
        # Set alarm button
        set_button = ttk.Button(set_frame, text="Set Alarm", command=self.set_alarm)
        set_button.pack(pady=10)
        
        # Alarms list
        alarms_frame = ttk.LabelFrame(parent, text="Active Alarms")
        alarms_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollable list for alarms
        scrollbar = ttk.Scrollbar(alarms_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.alarms_listbox = tk.Listbox(alarms_frame)
        self.alarms_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.alarms_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.alarms_listbox.yview)
        
        # Delete alarm button
        delete_button = ttk.Button(alarms_frame, text="Delete Selected", command=self.delete_alarm)
        delete_button.pack(pady=5)
    
    def setup_puzzle_tab(self, parent):
        # Puzzle display frame
        self.puzzle_frame = ttk.LabelFrame(parent, text="Current Puzzle")
        self.puzzle_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chess board display
        self.board_canvas = ChessBoardCanvas(self.puzzle_frame, bg="white")
        self.board_canvas.pack(pady=10)
        
        # Puzzle description
        self.puzzle_description = ttk.Label(self.puzzle_frame, text="No active puzzle", font=("Arial", 12, "bold"))
        self.puzzle_description.pack(pady=5)
        
        # Move entry
        move_frame = ttk.Frame(self.puzzle_frame)
        move_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(move_frame, text="Your move (e.g. e2e4):").pack(side="left", padx=5)
        self.move_entry = ttk.Entry(move_frame)
        self.move_entry.pack(side="left", expand=True, fill="x", padx=5)
        
        # Submit move button
        self.submit_button = ttk.Button(self.puzzle_frame, text="Submit Move", command=self.check_move)
        self.submit_button.pack(pady=10)
        self.submit_button.config(state="disabled")
        
        # Try a puzzle button
        try_button = ttk.Button(parent, text="Try a Random Puzzle", command=self.load_random_puzzle)
        try_button.pack(pady=10)
    
    def setup_settings_tab(self, parent):
        # Settings for the app
        sound_frame = ttk.LabelFrame(parent, text="Sound Settings")
        sound_frame.pack(fill="x", padx=10, pady=10)
        
        # Sound volume
        volume_frame = ttk.Frame(sound_frame)
        volume_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(volume_frame, text="Alarm Volume:").pack(side="left", padx=5)
        self.volume_scale = ttk.Scale(volume_frame, from_=0, to=100, orient="horizontal")
        self.volume_scale.set(70)  # Default volume
        self.volume_scale.pack(side="left", expand=True, fill="x", padx=5)
        
        # Other settings
        options_frame = ttk.LabelFrame(parent, text="Options")
        options_frame.pack(fill="x", padx=10, pady=10)
        
        # Auto-increase difficulty
        self.auto_increase_var = tk.BooleanVar(value=False)
        auto_increase_check = ttk.Checkbutton(options_frame, text="Auto-increase difficulty if puzzle not solved quickly", 
                                             variable=self.auto_increase_var)
        auto_increase_check.pack(anchor="w", padx=5, pady=5)
        
        # Snooze option
        self.snooze_var = tk.BooleanVar(value=True)
        snooze_check = ttk.Checkbutton(options_frame, text="Allow snooze with easier puzzle", 
                                      variable=self.snooze_var)
        snooze_check.pack(anchor="w", padx=5, pady=5)
        
        # Theme selection
        theme_frame = ttk.Frame(options_frame)
        theme_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(theme_frame, text="Board Theme:").pack(side="left", padx=5)
        self.theme_var = tk.StringVar(value="classic")
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var)
        theme_combo['values'] = ('classic', 'blue', 'green')
        theme_combo.pack(side="left", padx=5)
        theme_combo.bind("<<ComboboxSelected>>", self.change_theme)
        
        # About section
        about_frame = ttk.LabelFrame(parent, text="About")
        about_frame.pack(fill="x", padx=10, pady=10)
        
        about_text = "Chess Puzzle Alarm Clock\n"
        about_text += "Wake up your brain with chess puzzles!\n"
        about_text += "Version 1.0"
        
        ttk.Label(about_frame, text=about_text, justify="center").pack(padx=5, pady=5)
    
    def change_theme(self, event=None):
        """Change the board theme"""
        theme = self.theme_var.get()
        
        if theme == "classic":
            self.board_canvas.light_color = "#F0D9B5"
            self.board_canvas.dark_color = "#B58863"
        elif theme == "blue":
            self.board_canvas.light_color = "#DEE3E6"
            self.board_canvas.dark_color = "#8CA2AD"
        elif theme == "green":
            self.board_canvas.light_color = "#EEEED2"
            self.board_canvas.dark_color = "#769656"
        
        # Redraw the board
        self.board_canvas.draw_board()
    
    def set_alarm(self):
        try:
            hour = int(self.hour_spinbox.get())
            minute = int(self.minute_spinbox.get())
            difficulty = self.difficulty_var.get()
            
            if not 0 <= hour <= 23 or not 0 <= minute <= 59:
                messagebox.showerror("Invalid Time", "Please enter a valid time.")
                return
                
            # Get current time
            now = datetime.datetime.now()
            alarm_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time is in the past, set it for tomorrow
            if alarm_time <= now:
                alarm_time += datetime.timedelta(days=1)
            
            # Add to alarms list
            alarm_info = {
                "time": alarm_time,
                "difficulty": difficulty
            }
            
            self.alarms.append(alarm_info)
            self.update_alarms_list()
            
            messagebox.showinfo("Alarm Set", f"Alarm set for {alarm_time.strftime('%H:%M')}")
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for hour and minute.")
    
    def update_alarms_list(self):
        self.alarms_listbox.delete(0, tk.END)
        for alarm in self.alarms:
            self.alarms_listbox.insert(tk.END, f"{alarm['time'].strftime('%H:%M')} - {alarm['difficulty']}")
    
    def delete_alarm(self):
        selected = self.alarms_listbox.curselection()
        if selected:
            index = selected[0]
            del self.alarms[index]
            self.update_alarms_list()
    
    def check_alarms(self):
        while True:
            now = datetime.datetime.now()
            current_time = now.replace(second=0, microsecond=0)
            
            for alarm in self.alarms[:]:  # Make a copy to avoid modification issues
                if alarm["time"] <= now:
                    self.current_alarm = alarm
                    self.trigger_alarm(alarm)
                    self.alarms.remove(alarm)
                    self.update_alarms_list()
            
            time.sleep(15)  # Check every 15 seconds
    
    def trigger_alarm(self, alarm):
        # This would play a sound in a real implementation
        # For now, we'll just show a message and display a puzzle
        self.root.bell()  # Built-in bell sound
        
        # Show alarm notification
        self.alarm_active = True
        
        # Bring window to front
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.deiconify()  # Restore if minimized
        
        messagebox.showinfo("Alarm", "Time to wake up! Solve the chess puzzle to stop the alarm.")
        
        # Load a puzzle based on difficulty
        self.load_puzzle(alarm["difficulty"])
        
        # Start the alarm sound in a separate thread (simulated)
        self.alarm_thread = threading.Thread(target=self.play_alarm_sound, daemon=True)
        self.alarm_thread.start()
    
    def play_alarm_sound(self):
        # In a real implementation, this would play an actual sound file
        # For demonstration purposes, we'll just print to console and use the system bell
        while self.alarm_active:
            print("ALARM SOUND PLAYING")
            self.root.bell()
            time.sleep(3)  # Bell sound every 3 seconds
    
    def load_puzzle(self, difficulty):
        # Filter puzzles by difficulty
        suitable_puzzles = [p for p in self.puzzles if p["difficulty"] == difficulty]
        
        if not suitable_puzzles:
            # If no puzzles match the difficulty, use any puzzle
            suitable_puzzles = self.puzzles
        
        # Select a random puzzle
        self.current_puzzle = random.choice(suitable_puzzles)
        
        # Set up the chess board
        self.board = chess.Board(self.current_puzzle["fen"])
        self.expected_move = self.current_puzzle["solution"]
        
        # Update the UI
        self.puzzle_description.config(text=self.current_puzzle["description"])
        self.submit_button.config(state="normal")
        self.move_entry.delete(0, tk.END)
        
        # Show the board
        self.update_board_display()
    
    def load_random_puzzle(self):
        # Select a random puzzle for practice
        self.current_puzzle = random.choice(self.puzzles)
        
        # Set up the chess board
        self.board = chess.Board(self.current_puzzle["fen"])
        self.expected_move = self.current_puzzle["solution"]
        
        # Update the UI
        self.puzzle_description.config(text=self.current_puzzle["description"])
        self.submit_button.config(state="normal")
        self.move_entry.delete(0, tk.END)
        
        # Show the board
        self.update_board_display()
    
    def update_board_display(self):
        # Update board canvas with current position
        self.board_canvas.update_board(self.board)
    
    def check_move(self):
        user_move = self.move_entry.get().strip().lower()
        
        # Convert user input to chess move
        try:
            # Handle move in different formats
            if len(user_move) == 4:
                # Format: e2e4
                move = chess.Move.from_uci(user_move)
            elif len(user_move) == 5 and user_move[2] == 'x':
                # Format: e2xe4 (capture)
                move = chess.Move.from_uci(user_move[0] + user_move[1] + user_move[3] + user_move[4])
            else:
                # Try to parse as SAN (e.g., Nf3)
                move = self.board.parse_san(user_move)
            
            # Check if move is legal
            if move not in self.board.legal_moves:
                messagebox.showerror("Invalid Move", "That move is not legal in this position.")
                return
            
            # Check if move matches expected solution
            expected_move = chess.Move.from_uci(self.expected_move)
            
            if move == expected_move:
                # Correct move
                self.board.push(move)
                self.update_board_display()
                
                # If this was from an alarm, turn it off
                if self.alarm_active:
                    self.alarm_active = False
                    messagebox.showinfo("Alarm Stopped", "Great job! The alarm has been turned off.")
                    self.submit_button.config(state="disabled")
                else:
                    messagebox.showinfo("Correct", "That's the correct move! Puzzle solved.")
                    self.submit_button.config(state="disabled")
            else:
                # Wrong move
                messagebox.showerror("Wrong Move", "That's not the best move for this position. Try again!")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid chess move (e.g., e2e4 or Nf3).")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

def main():
    root = tk.Tk()
    app = ChessPuzzleAlarm(root)
    root.mainloop()

if __name__ == "__main__":
    main()