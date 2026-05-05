

def is_safe(board, row, col, n):
    for i in range(row):
        if board[i][col] == 'Q':
            return False

    i, j = row, col
    while i >= 0 and j >= 0:
        if board[i][j] == 'Q':
            return False
        i -= 1
        j -= 1

    i, j = row, col
    while i >= 0 and j < n:
        if board[i][j] == 'Q':
            return False
        i -= 1
        j += 1

    return True

def solve_queens(board, row, n):

    if row == n:
        return True

    for col in range(n):
        if is_safe(board, row, col, n):
            board[row][col] = 'Q' 

            if solve_queens(board, row + 1, n):
                return True

            board[row][col] = ' ' 
    return False

n = 6
values = [[' ' for i in range(n)] for i in range(n)]

if solve_queens(values, 0, n):
    print(f"Congrats! {n}x{n} queens has been set:\n")
    
    horizontal_line = "+" + "-----+" * n

    for i in range(n):
        print(horizontal_line)
        for j in range(n):

            print("|  ", values[i][j], end='  ')
        print("|")
    print(horizontal_line)
else:
    print("Solution not found.")