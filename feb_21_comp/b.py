K = int(input())

def find_next_square(K):
    n = K
    r = int(n**(1/2))
    while r * r != n:
        n += 1 
        r = int(n**(1/2))
    return n

