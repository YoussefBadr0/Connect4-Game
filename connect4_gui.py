import tkinter as tk
from tkinter import messagebox
import threading
import copy
from connect4_engine import Connect4  

class Connect4GUI:
    def __init__(self, master):
        self.master = master
        master.title("Connect 4")
        self.engine = Connect4()                  
        self.state = copy.deepcopy(self.engine.initial_grid)
        self.rows = self.engine.rows
        self.cols = self.engine.cols

        self.cells = [[None for _ in range(self.cols)] for __ in range(self.rows)]
        self.col_buttons = []
        self.ai_depth_var = tk.IntVar(value=4)

        # Design the top Frame (Buttons)
        top_frame = tk.Frame(master)
        top_frame.pack(pady=10)
        for c in range(self.cols):
            b = tk.Button(top_frame, text=str(c+1), width=4, command=lambda col=c: self.human_move(col))
            b.grid(row=0, column=c, padx=9)
            self.col_buttons.append(b)

        # Design the grid 
        board = tk.Frame(master, bg='black', bd=2)
        board.pack(padx=10, pady=6)
        for r in range(self.rows):
            for c in range(self.cols):
                lbl = tk.Label(board, text=" ", relief='ridge', width=4, height=2, bg='white', font=('Helvetica', 16))
                lbl.grid(row=r, column=c, padx=1, pady=1)
                self.cells[r][c] = lbl
        
        # Design the footer
        controls = tk.Frame(master)
        controls.pack(pady=6)
        tk.Label(controls, text="AI depth:").pack(side='left')
        tk.Spinbox(controls, from_=1, to=6, textvariable=self.ai_depth_var, width=3).pack(side='left', padx=6)
        tk.Button(controls, text="Reset", command=self.reset).pack(side='left', padx=6)

        self.status = tk.Label(master, text="Your turn (X)", font=('Helvetica', 12))
        self.status.pack(pady=6)

        self.update_ui()

    def update_ui(self):
        color_map = {" ": "white", "X": "red", "O": "yellow"}
        for r in range(self.rows):
            for c in range(self.cols):
                val = self.state[r][c]
                self.cells[r][c]['text'] = '●' if val != " " else " "
                self.cells[r][c]['bg'] = color_map[val]
        for c in range(self.cols):
            if self.state[0][c] != " ":
                self.col_buttons[c]['state'] = 'disabled'
            else:
                self.col_buttons[c]['state'] = 'normal'

    def human_move(self, col):
        if self.engine.current_player(self.state) != 'X':
            return
        if self.state[0][col] != " ":
            return
        action = ('X', col)
        new_state = self.engine.take_action(self.state, action)
        if new_state is None:
            return
        self.state = new_state
        self.update_ui()
        term = self.engine.check_terminal(self.state)
        if term != "Not terminal":
            self.end_game(term)
            return
        # disable buttons while Ai thinks
        for b in self.col_buttons:
            b['state'] = 'disabled'
        self.status['text'] = "Computer thinking..."
        threading.Thread(target=self.computer_move_thread, daemon=True).start() # Prevent Frozen window

    def computer_move_thread(self):
        actions = self.engine.available_actions(self.state)
        best_action = None
        best_val = None
        depth = max(1, int(self.ai_depth_var.get()))
        for action in actions:
            ns = self.engine.take_action(self.state, action)
            if ns is None: 
                continue
            val = self.engine.MinMax(ns, depth-1)
            if best_val is None:
                best_val = val
                best_action = action
            else:
                player = self.engine.current_player(self.state)
                if player == 'X' and val > best_val:
                    best_val = val
                    best_action = action
                if player == 'O' and val < best_val:
                    best_val = val
                    best_action = action
        if best_action is None and actions:
            best_action = actions[0]
        # apply move in main thread
        self.master.after(0, lambda: self.apply_computer(best_action))

    def apply_computer(self, action):
        if action is None:
            self.end_game(0)
            return
        self.state = self.engine.take_action(self.state, action)
        self.update_ui()
        term = self.engine.check_terminal(self.state)
        if term != "Not terminal":
            self.end_game(term)
            return

        for c in range(self.cols):
            if self.state[0][c] == " ":
                self.col_buttons[c]['state'] = 'normal'
            else:
                self.col_buttons[c]['state'] = 'disabled'
        self.status['text'] = "Your turn (X)"

    def end_game(self, term):
        for b in self.col_buttons:
            b['state'] = 'disabled'
        if term == 1:
            msg = "You (X) win!"
        elif term == -1:
            msg = "Computer (O) wins!"
        elif term == 0:
            msg = "Draw!"
        else:
            msg = f"Result: {term}"
        self.status['text'] = msg
        messagebox.showinfo("Game Over", msg)

    def reset(self):
        self.state = copy.deepcopy(self.engine.initial_grid)
        self.update_ui()
        self.status['text'] = "Your turn (X)"
        for c in range(self.cols):
            self.col_buttons[c]['state'] = 'normal' if self.state[0][c] == " " else 'disabled'

# run gui 
if __name__ == "__main__":
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()
