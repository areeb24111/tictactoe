import streamlit as st
import numpy as np
import random
import time

def check_winner(board, player):
    for i in range(5):
        if all([board[i][j] == player for j in range(5)]):  # Check rows
            return True
        if all([board[j][i] == player for j in range(5)]):  # Check columns
            return True
    if all([board[i][i] == player for i in range(5)]) or all([board[i][4 - i] == player for i in range(5)]):  # Check diagonals
        return True
    return False

def get_ai_move(board):
    empty_cells = [(i, j) for i in range(5) for j in range(5) if board[i][j] == ' ']
    return random.choice(empty_cells) if empty_cells else None

def main():
    st.title("Tic Tac Toe - 5x5")

    game_mode = st.selectbox("Select Game Mode", ["Multiplayer", "Single Player"])

    if "board" not in st.session_state:
        st.session_state.board = [[' ' for _ in range(5)] for _ in range(5)]
        st.session_state.current_player = "X"
        st.session_state.winner = None
        st.session_state.last_move_time = time.time()

    board = st.session_state.board

    if st.session_state.winner:
        st.success(f"{st.session_state.winner} wins! 🎉")
    elif all(cell != ' ' for row in board for cell in row):
        st.warning("It's a tie!")
    else:
        cols = st.columns(5)
        for i in range(5):
            for j in range(5):
                with cols[j]:
                    if st.button(f"{board[i][j] if board[i][j] != ' ' else ' '}", key=f"{i}-{j}") and board[i][j] == ' ':
                        board[i][j] = st.session_state.current_player
                        if check_winner(board, st.session_state.current_player):
                            st.session_state.winner = st.session_state.current_player
                        st.session_state.current_player = 'O' if st.session_state.current_player == 'X' else 'X'
                        st.session_state.last_move_time = time.time()

        # AI move for Single Player mode
        if game_mode == "Single Player" and st.session_state.current_player == "O" and not st.session_state.winner:
            ai_move = get_ai_move(board)
            if ai_move:
                time.sleep(1)  # Simulate AI thinking time
                board[ai_move[0]][ai_move[1]] = "O"
                if check_winner(board, "O"):
                    st.session_state.winner = "O"
                st.session_state.current_player = "X"
                st.session_state.last_move_time = time.time()

    # Timeout mechanism (5 seconds without a move)
    if time.time() - st.session_state.last_move_time > 5:
        st.session_state.winner = "Opponent Wins by Timeout!"

    # Restart Game Button
    if st.button("Restart Game", key="restart"):
        st.session_state.clear()
        st.rerun()  # ✅ Updated function

if __name__ == "__main__":
    main()
