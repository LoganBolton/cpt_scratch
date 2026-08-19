# Segment Tree: point update + range sum query
# query(left, right) is inclusive

class SegTree:
    def __init__(self, nums):
        self.n = len(nums)
        self.tree = [0] * (2 * self.n)
        self.build(nums)

    def build(self, nums):
        # put nums into leaves
        for i in range(self.n):
            self.tree[self.n + i] = nums[i]

        # build parents
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[i * 2] + self.tree[i * 2 + 1]

    # set nums[index] = val
    def update(self, index, val):
        index += self.n
        self.tree[index] = val

        while index > 1:
            index //= 2
            self.tree[index] = self.tree[index * 2] + self.tree[index * 2 + 1]

 # sum on inclusive range [left, right]
    def query(self, left, right):
        left += self.n
        right += self.n
        total = 0

        while left <= right:
            if left % 2 == 1:
                total += self.tree[left]
                left += 1
            if right % 2 == 0:
                total += self.tree[right]
                right -= 1

            left //= 2
            right //= 2

        return total

    def get(self, index):
        return self.tree[self.n + index]


# Example
nums = [1, 3, 5]
st = SegTree(nums)

print(st.query(0, 2))  # 9
st.update(1, 2)
print(st.query(0, 2))  # 8
print(st.get(1))       # 2