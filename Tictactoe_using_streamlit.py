import streamlit as st
import time
import random
import copy
from streamlit_autorefresh import st_autorefresh

# -------------------------------
# Constants and Initial Settings
# -------------------------------
TIME_LIMIT = 5  # seconds per move

# Always show the mode selectbox in the sidebar.
mode = st.sidebar.selectbox("Select Mode", ["Single Player", "Multi Player"], key="mode_select")

# If the mode has changed or is not yet set, update session_state and reset game.
if "mode" not in st.session_state or st.session_state.mode != mode:
    st.session_state.mode = mode
    st.session_state.board = [[" " for _ in range(5)] for _ in range(5)]
    st.session_state.turn = "X"  # X always goes first
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.last_move = time.time()
    st.session_state.sign = 0  # counts the number of moves

# Initialize other session state variables if not already set.
if "board" not in st.session_state:
    st.session_state.board = [[" " for _ in range(5)] for _ in range(5)]
if "turn" not in st.session_state:
    st.session_state.turn = "X"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winner" not in st.session_state:
    st.session_state.winner = None
if "last_move" not in st.session_state:
    st.session_state.last_move = time.time()
if "sign" not in st.session_state:
    st.session_state.sign = 0

# -------------------------------
# Auto-refresh every 1 second
# -------------------------------
st_autorefresh(interval=1000, limit=1000, key="game_autorefresh")

# -------------------------------
# Utility Functions
# -------------------------------
def check_winner(board, player):
    # Check all rows
    for row in board:
        if all(cell == player for cell in row):
            return True
    # Check all columns
    for col in range(5):
        if all(board[row][col] == player for row in range(5)):
            return True
    # Check the two main diagonals
    if all(board[i][i] == player for i in range(5)):
        return True
    if all(board[i][4 - i] == player for i in range(5)):
        return True
    return False

def is_full(board):
    return all(cell != " " for row in board for cell in row)

def pc_move():
    """
    Computer strategy:
      - Check if placing an 'O' or 'X' in any free cell wins (or blocks an opponent win)
      - Otherwise, picks a corner if available
      - Otherwise, picks randomly from the remaining cells
    """
    board = st.session_state.board
    possible_moves = [(i, j) for i in range(5) for j in range(5) if board[i][j] == " "]
    if not possible_moves:
        return None

    # Check for immediate win (or block)
    for let in ["O", "X"]:
        for move in possible_moves:
            board_copy = copy.deepcopy(board)
            board_copy[move[0]][move[1]] = let
            if check_winner(board_copy, let):
                return move

    # Prefer corners
    corners = [(0, 0), (0, 4), (4, 0), (4, 4)]
    corner_moves = [move for move in possible_moves if move in corners]
    if corner_moves:
        return random.choice(corner_moves)

    # Otherwise, pick any available move
    return random.choice(possible_moves)

def check_time_limit():
    """If more than TIME_LIMIT seconds have passed since the last move, end the game."""
    if st.session_state.game_over:
        return
    current_time = time.time()
    if current_time - st.session_state.last_move > TIME_LIMIT:
        # If sign is even, it was X's turn (so X timed out), awarding win to O; vice versa.
        st.session_state.winner = "O" if st.session_state.sign % 2 == 0 else "X"
        st.session_state.game_over = True

def make_move(row, col):
    """Process a move by updating the board, checking for a winner, and toggling turns."""
    if st.session_state.game_over:
        return
    board = st.session_state.board
    if board[row][col] != " ":
        return  # cell already filled

    # Check if time expired before processing the move
    check_time_limit()
    if st.session_state.game_over:
        return

    # Place the symbol and update move count and timer
    board[row][col] = st.session_state.turn
    st.session_state.sign += 1
    st.session_state.last_move = time.time()  # reset move timer

    # Check for win or tie
    if check_winner(board, st.session_state.turn):
        st.session_state.winner = st.session_state.turn
        st.session_state.game_over = True
        return
    if is_full(board):
        st.session_state.game_over = True
        st.session_state.winner = "Tie"
        return

    # Toggle turn: In single player mode, human is always 'X'
    st.session_state.turn = "O" if st.session_state.turn == "X" else "X"

def computer_turn():
    """Execute the computer's move immediately in single-player mode."""
    if st.session_state.game_over:
        return
    # Only run if in Single Player mode and it's computer's turn ("O")
    if st.session_state.mode == "Single Player" and st.session_state.turn == "O":
        move = pc_move()
        if move is not None:
            make_move(move[0], move[1])

# -------------------------------
# Main Game Logic & UI
# -------------------------------
st.title("Tic Tac Toe (5×5) with a 5-Second Move Timer")
st.write("Mode: " + st.session_state.mode)
st.write(f"Current turn: Player {st.session_state.turn}")

# Show the remaining time for the current move.
remaining_time = max(0, TIME_LIMIT - (time.time() - st.session_state.last_move))
st.write(f"Time remaining for current move: {remaining_time:.1f} seconds")

# Check time limit on every refresh
check_time_limit()

# In Single Player mode, only allow human clicks when it's the human's turn.
human_turn = True
if st.session_state.mode == "Single Player":
    human_turn = (st.session_state.turn == "X")

# Display the board as a grid of buttons.
for i in range(5):
    cols = st.columns(5)
    for j in range(5):
        cell_value = st.session_state.board[i][j]
        key = f"cell_{i}_{j}"
        # If cell is empty and it's a valid time for a human move, make it clickable.
        if cell_value == " " and not st.session_state.game_over and human_turn:
            if cols[j].button(" ", key=key):
                make_move(i, j)
                # In single-player mode, trigger the computer move immediately if game is not over.
                if st.session_state.mode == "Single Player" and not st.session_state.game_over:
                    computer_turn()
                # Instead of forcing an immediate rerun, rely on auto-refresh (or use rerun in try/except)
                try:
                    st.experimental_rerun()
                except Exception:
                    pass
        else:
            # Otherwise, display the cell value in a disabled button.
            cols[j].button(cell_value, key=key, disabled=True)

# If the game is over, display the result.
if st.session_state.game_over:
    if st.session_state.winner == "Tie":
        st.success("It's a tie!")
    else:
        st.success(f"Player {st.session_state.winner} wins!")
    if st.button("Restart Game"):
        st.session_state.board = [[" " for _ in range(5)] for _ in range(5)]
        st.session_state.turn = "X"
        st.session_state.game_over = False
        st.session_state.winner = None
        st.session_state.last_move = time.time()
        st.session_state.sign = 0
        st.experimental_rerun()
