from heapq import heappush, heappop, heapify
num_vertices, num_edges = 5,5
# src: dest, weight
edges = {
0: [(1, 1), (2,2)],
1: [(2, 3), (3,4)],
2: [(3, 5)],
}
mst = set() # set to store the edges in the MST
visited = {0} # set to store the visited vertices
total_weight = 0
curr_edges = [
    (cost, 0, dest)
    for dest, cost in edges[0]
]
heapify(curr_edges)
while curr_edges and len(visited) < num_vertices:
    cost, src, dest = heappop(curr_edges)
    if dest not in visited:
        visited.add(dest)
    mst.add((src, dest, cost))
    total_weight += cost
    for c_dest, c_cost in edges.get(dest, []):
        if c_dest not in visited:
            heappush(curr_edges, (c_cost, dest, c_dest))
            
    print("Total weight: " , total_weight)
    print(mst)