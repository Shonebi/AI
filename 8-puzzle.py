# Tài liệu tham khảo
# A. Artasanchez, P. Joshi, 
# Artificial Intelligence with Python, 
# 2nd Edition, Packt, 2020
# Trang 237-241


import tkinter as tk  # Thư viện GUI để tạo giao diện người dùng.
import numpy as np  # Thư viện để xử lý ma trận và các phép toán số học.
from simpleai.search import astar, SearchProblem  # Thư viện hỗ trợ thuật toán A* và định nghĩa bài toán tìm kiếm.
import random  # Thư viện dùng để tạo số ngẫu nhiên.

# Định nghĩa trạng thái mục tiêu của trò chơi (ô trống được biểu diễn bởi số 0).
GOAL = np.array([[1, 2, 3],  
                 [4, 5, 6],  
                 [7, 8, 0]])

# --- Các hàm tiện ích ---

# Tìm vị trí của một phần tử trong mảng numpy.
def get_location(arr, element):
    return tuple(np.argwhere(arr == element)[0])  # Trả về tọa độ (hàng, cột) của phần tử trong mảng.

# Chuyển đổi mảng numpy thành tuple để có thể dùng làm khóa trong tập hợp/hash table.
def array_to_tuple(arr):
    return tuple(map(tuple, arr))

# Chuyển đổi tuple ngược lại thành mảng numpy.
def tuple_to_array(tpl):
    return np.array([list(t) for t in tpl])

# Đếm số lượng nghịch thế (inversions) trong mảng (giúp kiểm tra tính giải được của trò chơi).
def count_inversions(puzzle):
    flat_puzzle = puzzle.flatten()  # Chuyển mảng thành một chiều.
    flat_puzzle = flat_puzzle[flat_puzzle != 0]  # Loại bỏ ô trống (0).
    inversions = 0
    for i in range(len(flat_puzzle)):  
        for j in range(i + 1, len(flat_puzzle)):  
            if flat_puzzle[i] > flat_puzzle[j]:  # Nếu vị trí trước lớn hơn vị trí sau thì có nghịch thế.
                inversions += 1
    return inversions

# Kiểm tra xem trò chơi có thể giải được không dựa vào số lượng nghịch thế.
def is_solvable(puzzle):
    return count_inversions(puzzle) % 2 == 0  # Nếu số nghịch thế chẵn thì trò chơi có thể giải được.

# Định nghĩa bài toán 8-puzzle thông qua lớp SearchProblem của thư viện simpleai.
class PuzzleSolver(SearchProblem):
    def __init__(self, initial_state):
        # Lưu vị trí đích (goal) của từng số trong mảng.
        self.goal_positions = {GOAL[i, j]: (i, j) for i in range(3) for j in range(3)}
        self.initial_state = initial_state  # Trạng thái ban đầu của bài toán.
        super().__init__(initial_state)  # Gọi hàm khởi tạo của lớp cha.

    # Xác định các hành động hợp lệ (di chuyển ô trống).
    def actions(self, cur_state):
        cur_state = tuple_to_array(cur_state)  # Chuyển trạng thái từ tuple sang mảng.
        row_empty, col_empty = get_location(cur_state, 0)  # Lấy vị trí ô trống.
        actions = []
        # Xác định các nước đi dựa trên vị trí ô trống.
        if row_empty > 0:  
            actions.append(cur_state[row_empty - 1, col_empty])  # Di chuyển lên.
        if row_empty < 2:  
            actions.append(cur_state[row_empty + 1, col_empty])  # Di chuyển xuống.
        if col_empty > 0:  
            actions.append(cur_state[row_empty, col_empty - 1])  # Di chuyển sang trái.
        if col_empty < 2:  
            actions.append(cur_state[row_empty, col_empty + 1])  # Di chuyển sang phải.
        return actions

    # Tính toán trạng thái mới sau khi thực hiện một hành động.
    def result(self, state, action):
        state = tuple_to_array(state)  # Chuyển đổi trạng thái từ tuple sang mảng.
        new_state = state.copy()  # Tạo bản sao của trạng thái.
        row_empty, col_empty = get_location(state, 0)  # Lấy vị trí ô trống.
        row_new, col_new = get_location(state, action)  # Lấy vị trí của số sẽ được hoán đổi.
        # Hoán đổi ô trống với số được chọn.
        new_state[row_empty, col_empty], new_state[row_new, col_new] = \
            new_state[row_new, col_new], new_state[row_empty, col_empty]
        return array_to_tuple(new_state)  # Chuyển đổi kết quả về dạng tuple.

    # Kiểm tra trạng thái hiện tại có phải là trạng thái mục tiêu không.
    def is_goal(self, state):
        return state == array_to_tuple(GOAL)  # So sánh trạng thái với mục tiêu.

    # Hàm heuristic: Tính tổng khoảng cách Manhattan của tất cả các số so với vị trí đích của chúng.
    def heuristic(self, state):
        state = tuple_to_array(state)  # Chuyển trạng thái từ tuple sang mảng.
        distance = 0
        for num in range(1, 9):  # Tính khoảng cách cho các số từ 1 đến 8.
            row_new, col_new = get_location(state, num)  # Vị trí hiện tại của số.
            row_goal, col_goal = self.goal_positions[num]  # Vị trí đích của số.
            distance += abs(row_new - row_goal) + abs(col_new - col_goal)  # Khoảng cách Manhattan.
        return distance

# Hàm giải bài toán 8-puzzle sử dụng thuật toán A*.
def solve_puzzle(initial_state):
    initial_state = array_to_tuple(initial_state)  # Chuyển trạng thái ban đầu thành tuple.
    solver = PuzzleSolver(initial_state)  # Khởi tạo bài toán.
    result = astar(solver)  # Giải bài toán bằng thuật toán A*.
    solution = [(action, state) for action, state in result.path()]  # Lưu lại các bước giải.
    return solution

# Hàm tạo một câu đố ngẫu nhiên (trạng thái ban đầu).
def generate_puzzle():
    numbers = list(range(1, 9)) + [0]  # Tập hợp các số từ 1 đến 8 và ô trống (0).
    random.shuffle(numbers)  # Xáo trộn ngẫu nhiên các số.
    return np.array(numbers).reshape(3, 3)  # Chuyển đổi thành ma trận 3x3.

# Hàm cập nhật giao diện lưới với trạng thái hiện tại của trò chơi.
def update_grid(puzzle, buttons):
    for i in range(3):
        for j in range(3):
            value = puzzle[i, j]  # Lấy giá trị tại ô (i, j).
            if value == 0:
                buttons[i][j].config(text='', bg="#ddd", state='disabled')  # Ô trống.
            else:
                buttons[i][j].config(text=str(value), bg="#f0f0f0", state='normal')  # Hiển thị số.

# Phần còn lại là xây dựng GUI bằng tkinter và xử lý các sự kiện trong trò chơi.

# Function to solve the puzzle and update the grid step by step
def solve_step_by_step(initial_state, buttons, status_label):
    # Cập nhật trạng thái của nhãn (status label) thành "Solving..." để người dùng biết quá trình đang diễn ra.
    status_label.config(text="Solving...")

    # Gọi hàm solve_puzzle để giải bài toán và nhận được các bước giải (là một danh sách các hành động và trạng thái)
    solution = solve_puzzle(initial_state)
    
    # Hàm con 'step' sẽ thực hiện từng bước trong giải pháp.
    def step(index=0):
        if index < len(solution):  # Kiểm tra nếu còn bước nào trong giải pháp
            action, state = solution[index]  # Lấy hành động và trạng thái của bước hiện tại
            update_grid(tuple_to_array(state), buttons)  # Cập nhật lưới giao diện với trạng thái mới
            root.after(1000, step, index + 1)  # Sử dụng root.after để trì hoãn 1 giây trước khi thực hiện bước tiếp theo
        else:
            # Nếu không còn bước nào, cập nhật trạng thái nhãn thành "Solved!" khi giải xong.
            status_label.config(text="Solved!")

    # Gọi hàm 'step' lần đầu tiên để bắt đầu quá trình giải từng bước.
    step()


# Tkinter GUI Setup
root = tk.Tk()
root.title("8-Puzzle Solver")
root.configure(bg="#e9ecef")

# Add a title
title_label = tk.Label(root, text="8-Puzzle Solver", font=("Arial", 24, "bold"), bg="#e9ecef")
title_label.pack(pady=10)

# Create the grid of buttons
frame = tk.Frame(root, bg="#e9ecef")
frame.pack(pady=10)
buttons = [[None for _ in range(3)] for _ in range(3)]
for i in range(3):
    for j in range(3):
        buttons[i][j] = tk.Button(frame, font=("Arial", 18, "bold"), width=4, height=2, bg="#f0f0f0")
        buttons[i][j].grid(row=i, column=j, padx=5, pady=5)

# Generate Button: Generates a new random puzzle
def on_generate():
    while True:
        puzzle = generate_puzzle()
        if is_solvable(puzzle):
            break
    update_grid(puzzle, buttons)
    status_label.config(text="Puzzle generated!", fg="black")

# Solve Button: Solves the current puzzle
def on_solve():
    current_state = np.array([[int(buttons[i][j]['text']) if buttons[i][j]['text'] != '' else 0 for j in range(3)] for i in range(3)])
    if not is_solvable(current_state):
        status_label.config(text="This puzzle is unsolvable!", fg="red")
        return
    solve_step_by_step(current_state, buttons, status_label)

# Add Generate and Solve buttons
button_frame = tk.Frame(root, bg="#e9ecef")
button_frame.pack(pady=10)
generate_button = tk.Button(button_frame, text="Generate", font=("Arial", 14), command=on_generate, bg="#007bff", fg="white")
generate_button.grid(row=0, column=0, padx=10)

solve_button = tk.Button(button_frame, text="Solve", font=("Arial", 14), command=on_solve, bg="#28a745", fg="white")
solve_button.grid(row=0, column=1, padx=10)

# Status label
status_label = tk.Label(root, text="Click Generate to start!", font=("Arial", 12), bg="#e9ecef", fg="#6c757d")
status_label.pack(pady=10)

# Initialize with a random puzzle
on_generate()

# Start the Tkinter main loop
root.mainloop()

