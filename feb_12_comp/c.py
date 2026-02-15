grid = []

for _ in range(5):
    line = input()
    grid.append(list(line))
    
num_kings = 0
    
dirs = [(2, 1), (2,-1), (-2, 1), (-2, -1), (1, 2), (-1, 2), (1, -2), (-1, -2)]
for r in range(5):
    for c in range(5):
        if grid[r][c] == '.':
            continue
        num_kings += 1
        for dir in dirs:
            dx = r + dir[0]
            dy = c + dir[1]
            if dx < 0 or dx >= 5 or dy < 0 or dy >= 5:
                continue
            if grid[dx][dy] == 'k':
                # print(r, c, dx, dy)
                print("invalid")
                exit()

if num_kings == 9: 
    print("valid")
else:
    print("invalid")