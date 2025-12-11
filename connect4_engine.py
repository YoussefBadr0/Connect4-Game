class Connect4:
    def __init__(self, rows=6, cols=7):
        self.rows = rows
        self.cols = cols
        self.initial_grid = [[" " for _ in range(cols)] for _ in range(rows)]

#region For run in jupyter
    # def display_grid(self, state):
    #     print()
    #     print(" ", end="")
    #     for c in range(self.cols):
    #         print(f" {c} ", end="")
    #     print()
    #     for r in range(self.rows):
    #         for c in range(self.cols):
    #             print(' ', state[r][c], ' ', sep='', end='')
    #             if c < self.cols - 1:
    #                 print('|', end='')
    #         print()
    #         if r < self.rows - 1:
    #             print("---+" * (self.cols - 1) + "---")
    #     print()
#endregion
    
    def take_action(self, current_state, action):
        player, col = action
        new_state = [row[:] for row in current_state] # Deep copy
        for r in range(self.rows - 1, -1, -1):
            if new_state[r][col] == " ":
                new_state[r][col] = player
                return new_state
        return None

    def current_player(self, state):
        count_X = 0
        count_O = 0
        for row in range(self.rows):
            for col in range(self.cols):
                symbol = state[row][col]
                if symbol == 'X':
                    count_X += 1
                elif symbol == 'O':
                    count_O += 1
        if count_X == count_O:
            return 'X'
        return 'O'

    def check_terminal(self, state):
        """
        Returns:
            1 if X wins
           -1 if O wins
            0 if draw
            "Not terminal" otherwise
        """
        # check bounds
        def in_bounds(r, c):
            return 0 <= r < self.rows and 0 <= c < self.cols

        directions = [(0,1), (1,0), (1,1), (1,-1)]  
        for r in range(self.rows):
            for c in range(self.cols):
                if state[r][c] == " ":
                    continue
                player = state[r][c]
                for dr, dc in directions:
                    count = 0
                    rr, cc = r, c
                    while in_bounds(rr, cc) and state[rr][cc] == player and count < 4:
                        count += 1
                        rr += dr
                        cc += dc
                    if count >= 4:
                        return 1 if player == 'X' else -1

        # check draw (no empty cells)
        for r in range(self.rows):
            for c in range(self.cols):
                if state[r][c] == " ":
                    return "Not terminal"
        return 0  

    
    def available_actions(self, current_state):
        actions = []
        player = self.current_player(current_state)
        for col in range(self.cols):
            if current_state[0][col] == " ":  
                actions.append((player, col))
        return actions

    
    def score_window(self, window, player):
        
        opp = 'O' if player == 'X' else 'X'
        score = 0
        if window.count(player) == 4:
            score += 1000
        elif window.count(player) == 3 and window.count(" ") == 1:
            score += 5
        elif window.count(player) == 2 and window.count(" ") == 2:
            score += 2

        if window.count(opp) == 3 and window.count(" ") == 1:
            score -= 4  
        return score

    def heuristic_evaluate(self, state):
        score = 0
        # center column control preference
        center_col = self.cols // 2
        center_count = sum(1 for r in range(self.rows) if state[r][center_col] == 'X')
        score += center_count * 3

        # horizontal
        for r in range(self.rows):
            row_array = state[r]
            for c in range(self.cols - 3):
                window = row_array[c:c+4]
                score += self.score_window(window, 'X')

        # vertical
        for c in range(self.cols):
            col_array = [state[r][c] for r in range(self.rows)]
            for r in range(self.rows - 3):
                window = col_array[r:r+4]
                score += self.score_window(window, 'X')

        # Main diagonal  [Top-left -> Bottom Right]
        for r in range(self.rows - 3):
            for c in range(self.cols - 3):
                window = [state[r+i][c+i] for i in range(4)]
                score += self.score_window(window, 'X')

        # Secondary diagonal  [top-Right -> Bottom Left]
        for r in range(self.rows - 3):
            for c in range(3, self.cols):
                window = [state[r+i][c-i] for i in range(4)]
                score += self.score_window(window, 'X')

        return score

    
    def MinMax(self, current_state, depth=4, alpha=float('-inf'), beta=float('inf')):
        terminal = self.check_terminal(current_state)
        if terminal != "Not terminal":
            if terminal == 1:
                return 10**6
            elif terminal == -1:
                return -10**6
            else:  
                return 0

        if depth == 0:
            return self.heuristic_evaluate(current_state)

        player = self.current_player(current_state)
        actions = self.available_actions(current_state)
        if player == 'X':
            value = float('-inf')
            for action in actions:
                next_state = self.take_action(current_state, action)
                if next_state is None:
                    continue
                new_val = self.MinMax(next_state, depth-1, alpha, beta)
                if new_val > value:
                    value = new_val
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value
        else:  # player == 'O'
            value = float('inf')
            for action in actions:
                next_state = self.take_action(current_state, action)
                if next_state is None:
                    continue
                new_val = self.MinMax(next_state, depth-1, alpha, beta)
                if new_val < value:
                    value = new_val
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value

# region For run in jupyter

    # def human_play(self, current_state):
    #     self.display_grid(current_state)
    #     player = self.current_player(current_state)
    #     print(f"Your turn, you are playing with {player}")
    #     while True:
    #         try:
    #             col = int(input(f"Choose column (0-{self.cols-1}): "))
    #             if col < 0 or col >= self.cols:
    #                 print("Column out of range. Try again.")
    #                 continue
    #             if current_state[0][col] != " ":
    #                 print("Column full. Choose another column.")
    #                 continue
    #             action = (player, col)
    #             new_state = self.take_action(current_state, action)
    #             self.display_grid(new_state)
    #             return new_state
    #         except ValueError:
    #             print("Invalid input. Enter a column number.")

    # def computer_play(self, current_state, depth=4):
    #     player = self.current_player(current_state)
    #     print(f"Computer turn, he is playing with {player}")
    #     actions = self.available_actions(current_state)
    #     best_value = None
    #     best_action = None
    #     for action in actions:
    #         next_state = self.take_action(current_state, action)
    #         if next_state is None:
    #             continue
    #         val = self.MinMax(next_state, depth-1)
    #         if best_value is None:
    #             best_value = val
    #             best_action = action
    #         else:
    #             if player == 'X' and val > best_value:
    #                 best_value = val
    #                 best_action = action
    #             if player == 'O' and val < best_value:
    #                 best_value = val
    #                 best_action = action

    #     if best_action is None:
    #         best_action = actions[0]
    #     player, col = best_action
    #     print(f"Computer decided to play in column {col}")
    #     new_state = self.take_action(current_state, best_action)
    #     return new_state


# Example simple play loop (human vs computer)
# if __name__ == "__main__":
#     game = Connect4()
#     state = game.initial_grid
#     while True:
#         # human
#         state = game.human_play(state)
#         term = game.check_terminal(state)
#         if term != "Not terminal":
#             print("Result:", term)
#             break
#         # computer
#         state = game.computer_play(state, depth=4)
#         term = game.check_terminal(state)
#         if term != "Not terminal":
#             print("Result:", term)
#             break
# endregion
