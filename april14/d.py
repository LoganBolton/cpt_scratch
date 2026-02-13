# make a dict of what every domino points to
# for every domino, add it to a seen
# do dfs from every position
# number of positions not seen is answer
from collections import *


num_tests = int(input())
for _ in range(num_tests):
    links = {}
    num_cities, num_pilots = map(int, input().split())
    
    for __ in range(num_pilots):
        first, second = map(int, input().split())
        if first not in links:
            links[first] = []
        if second not in links:
            links[second] = []
        links[first].append(second)
        links[second].append(first)
    
    # print(links)
    
    print(num_cities -1)

    
        
    
    
