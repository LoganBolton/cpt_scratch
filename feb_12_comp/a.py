import sys
alpha = set()
pangram_ex = "The quick brown fox jumps over the lazy dog"
for c in pangram_ex:
    if c == ' ': continue
    alpha.add(c.lower())
    
num_strs = int(input())
for _ in range(num_strs):
    curr_alpha = alpha.copy()
    string = input()
    for c in string:
        if c.isalpha():
            c = c.lower()
        else:
            continue
        
        if c in curr_alpha:
            curr_alpha.remove(c)
    if len(curr_alpha) == 0:
        print("pangram")
    else:
        missing = sorted(list(curr_alpha))
        print(f"missing {"".join(missing)}")


    
    