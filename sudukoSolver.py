"""This module finds the solution of a given sudoku problem with backtracking.

Example of the game board format,
board = [
    [7, 8, 0, 4, 0, 0, 1, 2, 0],
    [6, 0, 0, 0, 7, 5, 0, 0, 9],
    [0, 0, 0, 6, 0, 1, 0, 7, 8],
    [0, 0, 7, 0, 4, 0, 2, 6, 0],
    [0, 0, 1, 0, 5, 0, 9, 3, 0],
    [9, 0, 4, 0, 6, 0, 0, 0, 5],
    [0, 7, 0, 3, 0, 0, 0, 1, 2],
    [1, 2, 0, 0, 0, 7, 4, 0, 0],
    [0, 4, 9, 2, 0, 6, 0, 0, 7]
]
"""


def solve(board):
    """Function to solve the board with backtracking using recursion.

    Args:
        board (list): the game board.

    Returns:
        bool: True if solved completely, otherwise False.
    """

    # finding empty cell
    find = find_empty(board)
    if not find:
        return True
    else:
        row, col = find

    # adding values and checking validity
    for i in range(1, 10):
        if valid(board, i, (row, col)):
            board[row][col] = i

            if solve(board):
                return True

            board[row][col] = 0

    return False


def valid(board, num, pos):
    """Function to check validity of number placed.

    Args:
        board (list): the game board.
        num (int): number placed.
        pos (tuple): position it is placed at.

    Returns:
        bool: True if position is valid, otherwise False.
    """

    # Check every cell in row except current
    for i in range(len(board[0])):
        if board[pos[0]][i] == num and pos[1] != i:
            return False

    # Check every cell in column except current
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False

    # Check every cell in  box except current
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y*3, box_y*3 + 3):
        for j in range(box_x * 3, box_x*3 + 3):
            if board[i][j] == num and (i, j) != pos:
                return False

    return True


def print_board(board):
    """Function to print board.

    Args:
        board (list): the game board.
    """

    for i in range(len(board)):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - - - - ")

        for j in range(len(board[0])):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")

            if j == 8:
                print(board[i][j])
            else:
                print(str(board[i][j]) + " ", end="")


def find_empty(board):
    """Function to find empty cells in game board.

    Args:
        board (list): the current game board.

    Returns:
        (i, j) (tuple): empty position (row, column) if found, otherwise None.
    """

    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)  # row, col

    return None
