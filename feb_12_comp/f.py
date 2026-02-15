import heapq
# send one at a time through shortest dist graph. every time, remove a capacity from that node.
# When node reaches 0, rebuild shortest dist graph

n, m, s, t = map(int, input().split())
graph = {}
for i in range(n):
    graph[i] = []

for _ in range(m):
    u, v, c, w = map(int, input().split())
    graph[u].append((v,c,w))

print(graph)

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        curr_dist, node = heapq.heappop(pq)
        if curr_dist > dist[node]: #not closest
            continue

        for neighbor, capacity, cost in graph[node]:
            new_dist = curr_dist + cost 
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(pq,(new_dist, neighbor))
    print(dist)
    return dist, prev

short, prev = dijkstra(graph, s)
max_flow = -1
total_cost = 0
print(prev)

# go backwards to figure out path
def dfs(node, short, prev, max_flow, total_cost):
    if node == s:
        return

    prev_n = prev[node]
    edges = graph[prev_n]

    for i, edge in enumerate(edges):
        v, capacity, cost = edge

        if v == node:
            max_flow = max(capacity, max_flow)
            total_cost += cost       
            new_capacity = capacity -1

            edges[i] = (v, new_capacity, cost)

            if new_capacity == 0: # remove branch, remake graph
                print(f"Deleting {edges[i]}")
                del edges[i]
                short, prev = dijkstra(graph, s)
                
            max_flow, total_cost = dfs(prev[prev_n], short, prev, max_flow, total_cost)
    return max_flow, total_cost

max_flow, total_cost = dfs(t, short, prev, max_flow, total_cost)
print(max_flow, total_cost)