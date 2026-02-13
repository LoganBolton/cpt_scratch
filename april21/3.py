from collections import *

n, m, q, s= map(int, input().strip().split())

graph = {}
for _ in range(m):
    n1, n2, w = map(int, input().split())
    if n1 not in graph:
        graph[n1] = []
    if n2 not in graph:
        graph[n2] = []
        
    graph[n1].append([n2, w])
    graph[n2].append([n1, w])
    
for _ in range(q):
    
    queue = [graph[s]].dequeue