n, p = map(int, input().split())
cost = list(map(int, input().split()))

profit = 0
max_profit = 0

for i in range(len(cost)):
    curr = cost[i]
    # print(i, curr, max_profit)
    if profit + (curr - p) < 0:
        profit = 0
        continue
    
    profit += (curr - p)
    max_profit = max(max_profit, profit)
print(max_profit)
    
# -2, 15, -14, 60, -5, 1