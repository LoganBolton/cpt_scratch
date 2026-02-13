import sys
input = sys.stdin.readline

n = int(input())
words = [input().strip() for _ in range(n)]

content = {i: [words[i]] for i in range(n)}

for _ in range(n - 1):
    line = input()
    if not line.strip():
        continue
    try:
        a, b = map(int, line.strip().split())
        a -= 1
        b -= 1
        if a < 0 or b < 0 or a >= n or b >= n:
            continue
        content[a].extend(content[b])
        content[b] = []
    except Exception as e:
        print(f"Skipping line due to error: {e}")
        continue

for lst in content.values():
    if lst:
        print(''.join(lst))
        break
