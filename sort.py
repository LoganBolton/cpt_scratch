# 3 3
# oTs
# nwi
# eox
# 3 4
# xAxa
# yByb
# zCyc
# 0 0
R, C = map(int, input().split())

while R != 0 and C != 0:
    strings = [""] * C
    
    for r in range(R):
        row = input()
        for c in range(C):
            strings[c] += row[c]
    
    # print(strings)
    strings.sort(key=str.lower)
    # print(strings)
    for r in range(R):
        for c in range(C):
            print(strings[c][r], end='')
        print()
        
    print()
    R, C = map(int, input().split())
