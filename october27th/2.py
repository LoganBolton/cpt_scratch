
n_socks = int(input())
main = list(map(int, input().split()))
# print(n_socks, main)


aux = []

res = 0

n = len(main)

while len(main) > 0 or len(aux) > 0:
    last_main_n = len(main)
    while len(main) > 0:
        # print(main, aux)
        res += 1
        top_main = main.pop()
        if len(aux) == 0:
            aux.append(top_main)
            continue
        top_aux = aux.pop()
        
        if top_main != top_aux:
            aux.append(top_aux)
            aux.append(top_main)

    # if len(aux) == last_main_n:
    #     print("impossible")
    #     exit()
        
    # last_aux_n = len(aux)

    while len(aux) > 0:
        res += 1
        top_aux = aux.pop()
        if len(main) == 0:
            main.append(top_aux)
            continue
        top_main = main.pop()
        
        if top_main != top_aux:
            main.append(top_main)
            main.append(top_aux) 
        
    
    if len(main) == last_main_n:
        print("impossible")
        exit()

print(res)