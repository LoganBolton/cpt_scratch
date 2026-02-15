import heapq
import uuid
# send one at a time through shortest dist graph. every time, remove a capacity from that node.
# When node reaches 0, rebuild shortest dist graph

n, m, s, t = map(int, input().split())
graph = {}
for i in range(n):
    graph[i] = []

for _ in range(m):
    u, v, c, w = map(int, input().split())
    id = uuid.uuid4().hex

    graph[u].append((v,c,w,id))

# print(graph)

def dijkstra(graph, start):
    dist = {node: float('inf') for node in graph}
    prev = {node: None for node in graph}
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        curr_dist, node = heapq.heappop(pq)
        if curr_dist > dist[node]: #not closest
            continue

        for neighbor, capacity, cost, id in graph[node]:
            new_dist = curr_dist + cost 
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                prev[neighbor] = node
                heapq.heappush(pq,(new_dist, neighbor))
    print(f"graph: {graph}")
    print(f"dist: {dist}")
    print(f"prev: {prev}")
    return dist, prev

short, prev = dijkstra(graph, s)
total_cost = 0
# print(prev)

# go backwards to figure out path
def dfs(node, short, prev, curr_flow, total_cost, deleted, path):
    # print(node, total_cost, deleted)
    print(node, total_cost, curr_flow, path)
    # path.append(node)
    if node == s:
        for node, idx in deleted:
            # print(deleted, delete)
            # print(node, idx, deleted)
            del graph[node][idx] 
        if len(deleted) > 0:
            # print(deleted)
            short, prev = dijkstra(graph, s)

        return curr_flow, total_cost, short, prev, deleted, path

    prev_n = prev[node]
    edges = graph[prev_n]

    for i, edge in enumerate(edges):
        v, capacity, cost, id = edge

        if v == node:
            # print((v,capacity, cost))
            curr_flow = max(capacity, curr_flow)
            total_cost += cost       
            new_capacity = capacity -1

            edges[i] = (v, new_capacity, cost, id)

            path_copy = path.copy()

            if new_capacity == 0: # remove branch, remake graph
                # print(f"Deleting {graph[prev_n][i], prev_n, i}")
                future_delete = (prev_n, i) 
                deleted.append(future_delete)

            # print(node, v)
            if prev_n is not None:    
                curr_flow, total_cost, short, prev, deleted, path = dfs(prev_n, short, prev, curr_flow, total_cost, deleted, path_copy+[id])

    return curr_flow, total_cost, short, prev, deleted, path

seen = set()

max_flow = 0
two_hop_not_taken = True
while short[t] != float('inf'): 
    min_flow, curr_cost, short, prev, deleted, path = dfs(t, short, prev, 0, 0, [], [])

    new_path = True
    # print("-----")
    # print(path) 
    for edge in path:
        if edge in seen:
            new_path = False
            break
        seen.add(edge)
    if new_path:
        # print("new path", path, min_flow)
        max_flow += min_flow

    total_cost += curr_cost

# print("----------")
print(max_flow, total_cost)