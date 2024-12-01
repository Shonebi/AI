import streamlit as st
import numpy as np
from simpleai.search import astar, SearchProblem
import random
import time

# Define the Goal state
GOAL = np.array([[1, 2, 3],
                 [4, 5, 6],
                 [7, 8, 0]])  # Using 0 for empty space ('e')


# Helper Functions
def get_location(arr, element):
    return tuple(np.argwhere(arr == element)[0])


def array_to_tuple(arr):
    """Convert a numpy array to a tuple of tuples to make it hashable."""
    return tuple(map(tuple, arr))


def tuple_to_array(tpl):
    """Convert a tuple of tuples back to a numpy array."""
    return np.array([list(t) for t in tpl])


# Check if a puzzle is solvable
def is_solvable(puzzle):
    flat_puzzle = puzzle.flatten()
    inversions = 0
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] > flat_puzzle[j] and flat_puzzle[j] != 0:
                inversions += 1
    return inversions % 2 == 0


# Puzzle Solver Class using simpleai
class PuzzleSolver(SearchProblem):
    def __init__(self, initial_state):
        self.goal_positions = {}
        for i in range(3):
            for j in range(3):
                self.goal_positions[GOAL[i, j]] = (i, j)
        self.initial_state = initial_state
        super().__init__(initial_state)

    def actions(self, cur_state):
        cur_state = tuple_to_array(cur_state)
        row_empty, col_empty = get_location(cur_state, 0)
        actions = []
        if row_empty > 0:
            actions.append(cur_state[row_empty - 1, col_empty])
        if row_empty < 2:
            actions.append(cur_state[row_empty + 1, col_empty])
        if col_empty > 0:
            actions.append(cur_state[row_empty, col_empty - 1])
        if col_empty < 2:
            actions.append(cur_state[row_empty, col_empty + 1])
        return actions

    def result(self, state, action):
        state = tuple_to_array(state)
        new_state = state.copy()
        row_empty, col_empty = get_location(state, 0)
        row_new, col_new = get_location(state, action)
        new_state[row_empty, col_empty], new_state[row_new, col_new] = \
            new_state[row_new, col_new], new_state[row_empty, col_empty]
        return array_to_tuple(new_state)

    def is_goal(self, state):
        return state == array_to_tuple(GOAL)

    def heuristic(self, state):
        state = tuple_to_array(state)
        distance = 0
        for num in range(1, 9):
            row_new, col_new = get_location(state, num)
            row_goal, col_goal = self.goal_positions[num]
            distance += abs(row_new - row_goal) + abs(col_new - col_goal)
        return distance


def solve_puzzle(initial_state):
    initial_state = array_to_tuple(initial_state)
    solver = PuzzleSolver(initial_state)
    result = astar(solver)
    return [(action, state) for action, state in result.path()]


def generate_puzzle():
    numbers = list(range(1, 9)) + [0]
    random.shuffle(numbers)
    return np.array(numbers).reshape(3, 3)


# Streamlit App
st.title("🎮 8-Puzzle Solver")
st.markdown("Solve the 8-puzzle interactively with a beautiful interface!")

# Session state
if "puzzle" not in st.session_state:
    st.session_state.puzzle = generate_puzzle()
    st.session_state.solution = None

def display_puzzle(puzzle):
    cols = st.columns(3)  # Tạo bố cục 3 cột
    for i in range(3):
        for j in range(3):
            num = puzzle[i, j]
            bg_color = '#ADD8E6' if num == 0 else '#FFD700'  # Màu ô (xanh nhạt cho 0, vàng cho số khác)
            display_text = " " if num == 0 else str(num)  # Hiển thị khoảng trống cho 0
            cols[j].markdown(
                f"""
                <div style="
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 50px; width: 50px;
                    background-color: {bg_color};
                    border: 1px solid black;
                    border-radius: 5px;
                    font-size: 20px;
                    font-weight: bold;">
                    {display_text}
                </div>
                """,
                unsafe_allow_html=True,
            )


if st.button("🔄 Generate New Puzzle"):
    st.session_state.puzzle = generate_puzzle()
    st.session_state.solution = None

display_puzzle(st.session_state.puzzle)

if st.button("🧩 Solve Puzzle"):
    if is_solvable(st.session_state.puzzle):
        st.session_state.solution = solve_puzzle(st.session_state.puzzle)
        st.write("Solving the puzzle...")
        placeholder = st.empty()  # For animating the puzzle

        # Animate solution
        for _, state in st.session_state.solution:
            current_puzzle = tuple_to_array(state)
            with placeholder.container():
                display_puzzle(current_puzzle)
            time.sleep(0.5)  # Pause between steps for animation
        st.success("Puzzle solved!")
    else:
        st.error("This puzzle configuration is unsolvable!")