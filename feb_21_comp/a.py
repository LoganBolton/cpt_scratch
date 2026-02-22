import sys
values = {}
rev_values = {}
# line = str(input())
# while line:
for line in sys.stdin:
    line =  line.rstrip("\n")

    # print(f"line: {line}")
    inputs = line.split()
    # print(f"inputs: {inputs}")

    if inputs[0] == "def":
        x = inputs[1]
        y = int(inputs[2])

        if x in values:
            old = values[x]
            if rev_values.get(old) == x:
                del rev_values[old]

        values[x] = y
        rev_values[y] = x
    elif inputs[0] == "clear":
        values = {}
        rev_values = {}

    elif inputs[0] == "calc":
        output = 0
        prev_opp = '+'
        known_vars = True 
        
        for i in range(1, len(inputs)-1):
            # print(inputs[i])
            if inputs[i] == '+':
                prev_opp = '+'
                continue
            elif inputs[i] == '-':
                prev_opp = '-'
                continue

            if inputs[i] not in values:
                print(f"{' '.join(inputs[1:])} unknown")
                known_vars = False
                break 

            val = int(values[inputs[i]])
            if prev_opp == '+':
                output += val
            elif prev_opp == '-':
                output -= val
            else:
                print("unknown")
        # print(inputs, output, rev_values)

        if output in rev_values and known_vars:
            print(f"{' '.join(inputs[1:])} {rev_values[output]}")
        elif known_vars:
            print(f"{' '.join(inputs[1:])} unknown")
        # print()

        # break
    # break
    # line = str(input())
