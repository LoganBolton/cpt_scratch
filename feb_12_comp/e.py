inf = 999999
MAX = 2500
G = []
V = int(input())
for _ in range(V):
    line = input()
    lst = list(map(int,line.split()))
    G.append(lst)
    
S = [[0 for _ in range(MAX)] for _ in range(MAX)]
n = V
def main():
    global n
    cost = prims()

def prims():
    global n
    C = [[0 for _ in range(MAX)] for _ in range(MAX)]
    u, v = 0, 0
    min_dist = 0
    dist = [0 for _ in range(MAX)]
    from_ = [0 for _ in range(MAX)]
    visited = [0 for _ in range(MAX)]
    ne = 0
    min_cost = 0
    i = 0
    j = 0
    for i in range(n):
        for j in range(n):
            if G[i][j] == 0:
                C[i][j] = inf
            else:
                C[i][j] = G[i][j]
            S[i][j] = 0
    dist[0] = 0
    visited[0] = 1
    for i in range(1, n):
        dist[i] = C[0][i]
        from_[i] = 0
        visited[i] = 0
    min_cost = 0
    ne = n - 1
    while ne > 0:
        min_dist = inf
        for i in range(1, n):
            if visited[i] == 0 and dist[i] < min_dist:
                v = i
                min_dist = dist[i]
        u = from_[v]
        S[u][v] = dist[v]
        S[v][u] = dist[v]
        ne -= 1
        visited[v] = 1
        for i in range(n):
            if visited[i] == 0 and C[i][v] < dist[i]:
                dist[i] = C[i][v]
                from_[i] = v
        min_cost += C[u][v]
        print(str(u+1) + ' ' + str(v+1))
    return 
#calling  the main() method
main()