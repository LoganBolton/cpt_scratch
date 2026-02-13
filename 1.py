class Graph:
    def __init__(self, size):
        self.adj_matrix = [[0] * size for _ in range(size)]
        self.size = size
        self.vertex_data = [''] * size

    def add_edge(self, u, v, weight):
        if 0 <= u < self.size and 0 <= v < self.size:
            self.adj_matrix[u][v] = weight
            self.adj_matrix[v][u] = weight  # For undirected graph

    def add_vertex_data(self, vertex, data):
        if 0 <= vertex < self.size:
            self.vertex_data[vertex] = data

    def prims_algorithm(self):
        in_mst = [False] * self.size
        key_values = [float('inf')] * self.size
        parents = [-1] * self.size

        key_values[0] = 0  # Starting vertex

        # print("Edge \tWeight")
        for _ in range(self.size):
            u = min((v for v in range(self.size) if not in_mst[v]), key=lambda v: key_values[v])

            in_mst[u] = True

            if parents[u] != -1:  # Skip printing for the first vertex since it has no parent
                # print(f"{self.vertex_data[parents[u]]}-{self.vertex_data[u]} \t{self.adj_matrix[u][parents[u]]}")
                p1 = int(self.vertex_data[parents[u]])
                p2 = int(self.vertex_data[u])
                print(f"{p1} {p2}")

            for v in range(self.size):
                if 0 < self.adj_matrix[u][v] < key_values[v] and not in_mst[v]:
                    key_values[v] = self.adj_matrix[u][v]
                    parents[v] = u

# N = 4

# matrix = [
#     [0, 1, 1, 2],
#     [1, 0, 2, 3],
#     [1, 2, 0, 3],
#     [2, 3, 3, 0]
# ]
N = int(input())
g = Graph(N)
matrix = []
for i in range(N):
    row = list(map(int, input().split()))
    matrix.append(row)


for i in range(N):
    g.add_vertex_data(i, str(i+1))
    for j in range(N):
        if i == j:
            continue
        g.add_edge(i, j, matrix[i][j])

g.prims_algorithm()