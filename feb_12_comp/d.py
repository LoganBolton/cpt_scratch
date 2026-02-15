# two deques 
# if add front, push to front deque
# if middle, append te back of front deque
# if bcak, append to end of last deque

# 9
# push_back 9
# push_front 3
# push_middle 5
# get 0: 3
# get 1: 5 
# get 2: 9
# push_middle 1
# get 1 : 5
# get 2: 1


# 3 5   9
# 


from collections import deque

first = deque()
last = deque()


def push_front(first, last, val):
    first.appendleft(val)
    return first, last

def push_middle(first,last,val):
    if len(first) == 0 or (len(first) + len(last)) % 2 != 0: # odd:
        first.append(val)
    else:
        prev_middle = first.pop()
        first.append(val)
        last.appendleft(prev_middle)
    return first, last

def push_back(first, last, val):
    last.append(val)
    return first, last

def get_i(first,last,i):
    if i < len(first)-1:
        return first[i]
    else:
        return last[len(first)-1-i]

n = int(input())

for _ in range(n):
    line = input()
    command, value = line.split(' ')
    print(command, value)
    if command == "push_back": 
        push_back(first, last, value)
    if command == "push_front": 
        push_front(first, last, value)
    if command == "push_middle": 
        push_middle(first, last, value)
    if command == "get": 
        print(get_i(first, last, int(value)))
    print(first, last)
    print()
    
