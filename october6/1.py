true_max, true_min = float('inf'), float('-inf')

def break_game():
    input_line = input()
    while input_line != "0":
        input_line = input()

number = int(input())
while number != 0:
    guess = str(input())
    print(true_min, true_max, number, guess, )
    
    if guess == "too high":
        if number <= true_max:
            print("Stan is dishonest")
            break_game()
            true_max, true_min = float('inf'), float('-inf')
            continue
        true_max = min(true_max, number)
        true_max -= 1
    elif guess == "too low":
        if number >= true_min:
            print("Stan is dishonest")
            break_game
            true_max, true_min = float('inf'), float('-inf')
            continue
        true_min = max(true_min, number)
        true_min += 1
    elif guess == "right on":
        true_max, true_min = float('inf'), float('-inf')

        
    
    number = int(input())
