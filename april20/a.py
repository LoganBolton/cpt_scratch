num_cases = int(input())

def class_to_string(cls):
    if '-' in cls:
        rank_arr = cls.split('-')
    else:
        rank_arr = [cls]
    rank = ""
    
    for r in rank_arr:
        if r == "lower":
            rank += "3"
        elif r == "middle":
            rank += "2"
        elif r == "upper":
            rank += "1"
            
    for _ in range(30-len(rank_arr)):
        rank += "3"
    return rank

my_dic = {}
for i in range(num_cases):
    num_names = int(input())
    for _ in range(num_names):
        part_str = input()
        part_arr = part_str.split(' ')
        name = part_arr[0][:-1]
        class_str = class_to_string(part_arr[1])
        my_dic[name] = class_str
    
    for key in dict(sorted(my_dic.items(), key=lambda item: item[1])):
        print(key)
    print(my_dic)
    print("==============================")

    my_dic = {}
    # print(my_dic)
# print(my_dic)
        