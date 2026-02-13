# DRM Encryption is a new kind of encryption. Given an encrypted string (which we’ll call a DRM message), the decryption process involves three steps: Divide, Rotate and Merge. This process is described in the following example with the DRM message “EWPGAJRB”:

# Divide
# – First, divide the message in half to “EWPG” and “AJRB”.

# Rotate
# – For each half, calculate its rotation value by summing up the values of each character (
# ). The rotation value of “EWPG” is 
# . Rotate each character in “EWPG” 
#  positions forward (wrapping from Z to A when necessary) to obtain the new string “ZRKB”. Following the same process on “AJRB” results in “BKSC”.

# Merge
# – The last step is to combine these new strings (“ZRKB” and “BKSC”) by rotating each character in the first string by the value of the corresponding character in the second string. For the first position, rotating ‘Z’ by ‘B’ means moving it forward 1 character, which wraps it around to ‘A’. Continuing this process for every character results in the final decrypted message, “ABCD”.

# Input
# The input contains a single DRM message to be decrypted. All characters in the string are uppercase letters and the string’s length is even and 
# .

# Output
# Display the decrypted DRM message.

# Sample Input 1	Sample Output 1
# EWPGAJRB
# ABCD


word = str(input())
word1 = word[0:len(word)//2]
word2 = word[len(word)//2:]

def rotate(word):
    # figure out how much to rotate
    rotation_amnt = 0
    OFFSET = 65
    for c in word:
        letter_val = ord(c) - OFFSET
        # print(c, letter_val)
        rotation_amnt += letter_val
        
    # rotate word
    res = ""
    # rotation_amnt %= 26
    # print(rotation_amnt)
    for i in range(len(word)):
        old_c = ord(word[i])
        new_val = old_c + rotation_amnt - OFFSET
        # print(new_val)
        res += chr((new_val%26)+OFFSET)
        # print(res)
        
    return res
    
def merge(r_w1, r_w2):
    res = ""
    OFFSET = 65
    for i in range(len(word1)):
        c1 = ord(r_w1[i]) - OFFSET
        c2 = ord(r_w2[i]) - OFFSET
        
        new_c = (c1 + c2) % 26
        # print(c1, c2, new_c)
        res += chr(new_c + OFFSET)
    return res
# print(word1, word2)
# print(rotate(word1))
# print(rotate(word2))
rot_1 = rotate(word1)
rot_2 = rotate(word2)

print(merge(rot_1, rot_2))