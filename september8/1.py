from collections import *

rows, cols = map(int, input().split())

grid = []
for i in range(rows):
    row = list(input().strip())
    grid.append(row)

count = 0

queue = deque()
for r in range(rows):
    for c in range(cols):
        if grid[r][c] == '.' or grid[r][c] == '0': # visited or blank
            continue
        grid[r][c] == '0'
        
        queue.append((r,c))
        count += 1
        dirs = [(1, 0), (1,1), (0,1), (-1,0), (0, -1), (-1, -1), (1, -1), (-1, 1)]
        while queue:
            y, x = queue.popleft()
            if grid[y][x] == '.' or grid[y][x] == '0':
                continue
            
            
            for dy, dx in dirs:
                new_y, new_x = y+dy, x+dx
                if new_y < 0 or new_y >= rows:
                    continue
                if new_x < 0 or new_x >= cols:
                    continue
                
                if grid[new_y][new_x] == "1":
                    queue.append((new_y, new_x))

print(count)