num_lines = int(input())

def find_next_sqrt(L):
    i = L
    while i % (i**(1/2)) != 0:
        i += 1
    return i
# r2 -> col2
# r1 -> col3
def rotate_grid(grid):
    square = len(grid)
    new_grid = [['0'] * square for _ in range(square)]

    for r in range(square-1, 0-1, -1):
        for c in range(square):
            val = grid[r][c]
            new_r = c
            new_c = square-1-r
            # print(r,c,"\t",new_r,new_c, val)

            new_grid[new_r][new_c] = val
        # print(new_grid)
    return new_grid
    
for _ in range(num_lines):
    line = input()
    L = len(line)
    M = find_next_sqrt(L)
    grid = []
    str_idx = 0
    square_length = int(M**(1/2))
    for i in range(square_length):
        row = []
        for j in range(square_length):
            if str_idx < L:
                row.append(line[str_idx])
                str_idx += 1
            else:
                row.append('*')
        grid.append(row)
    rotated_grid = rotate_grid(grid)
    res = []
    for row in rotated_grid:
        for c in row:
            if c != '*':
                res.append(c)
    print(''.join(res))
    # print(grid)
    # print(rotated_grid)
    
    