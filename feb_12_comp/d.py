# two deques 
# if add front, push to front deque
# if middle, append te back of front deque
# if bcak, append to end of last deque

#maybe enforce that both arrays have to be basically the same size?
# if you want to add to middle and second array is 1 bigger, move one to the left and add to the top

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
# 3 5   1 9


#       1

from collections import deque
import sys

def balance_bias(first, last):
    # right side bigger bias
    if len(first) - len(last) == 0:
        return
    if len(first)-len(last) > 0: # left is larger
        prev_middle = first.pop()
        last.appendleft(prev_middle)
    if len(last) - len(first) > 1: # right is too large
        prev_middle = last.popleft()
        first.append(prev_middle)

def push_front(first, val):
    first.appendleft(val)

def push_middle(first,last,val):
    if len(first) < len(last): # if left smaller, move last front to first back and add val to last front
        prev_middle = last.popleft()
        first.append(prev_middle)
        last.appendleft(val)
    elif len(first) == len(last):
        last.appendleft(val)
    
    first = first
    last = last
    

def push_back(last, val):
    last.append(val)

# 2
def get_i(first,last,i):
    if i < len(first): # ex: idx 0 is less than size 1
        return first[i]
    else:
        prev_idxs = len(first)
        return last[i-prev_idxs]

data = sys.stdin.buffer.read().split()
it = iter(data)

first = deque()
last = deque()
n = int(next(it))

out = bytearray()

for _ in range(n):
    command = next(it)
    value = next(it)

    # line = input()
    # command, value = line.split(' ')
    if command == b'push_back': 
        push_back(last, value)
        balance_bias(first, last)
    if command == b'push_front': 
        push_front(first, value)
        balance_bias(first, last)
    if command == b'push_middle': 
        push_middle(first, last, value)
        balance_bias(first, last)
    if command == b'get': 
        out += get_i(first, last, int(value)) + b'\n'
    # print(command, value)
    # print(first, last)
    # print()

sys.stdout.buffer.write(out)
