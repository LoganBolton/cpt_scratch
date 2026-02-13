# make a dict of what every domino points to
# for every domino, add it to a seen
# do dfs from every position
# number of positions not seen is answer


num_tests = int(input())
for _ in range(num_tests):
    seen = set()
    num_cities = int(input())
    
    for __ in range(num_cities):
        city = input()
        seen.add(city)
    
    print(len(seen))
        
