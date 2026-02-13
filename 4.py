# 0 0 1 0 0 0
# 0 0 0 1 1 0
num_bits, num_instruct = map(int, input().split())

a = [0] * num_bits
# print(a)

for i in range(num_instruct):
    instruction = input().split()
    # print(instruction)
    if instruction[0] == 'F':
        i = int(instruction[1])-1
        if a[i] == 0:
            a[i] = 1
        else:
            a[i] = 0
        print(a)
    elif instruction[0] == 'C':
        i1 = int(instruction[1])
        i2 = int(instruction[2])
        count = 0
        print(i1, i2)
        for i in range(i1, i2):
            # print(i)
            if a[i-1] == 1:
               count += 1
        print(count)