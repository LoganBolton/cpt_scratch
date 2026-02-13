# make a dict of what every domino points to
# for every domino, add it to a seen
# do dfs from every position
# number of positions not seen is answer
from collections import defaultdict


num_tests = int(input())
for _ in range(num_tests):
    links = {}
    seen = set()
    num_dominoes, num_lines = map(int, input().split())
    
    for __ in range(num_lines):
        first, second = map(int, input().split())
        links[first] = second
    
    # print(links)
    for i in range(num_dominoes):
        if i not in links:
            continue
        else:
            seen.add(links[i])
    print(num_dominoes-len(seen))
        
