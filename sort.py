import random
from collections import deque
import threading


# TODO comb sort


class Sort:
    def __init__(self):
        self.queue = deque()  # appendleft, pop
        self.data_lock = threading.Lock()
        self.data = []
        self.algorithm = None
        self.run_lock = threading.Lock()
        self.run = False

    def clear(self):
        self.run = False
        self.queue.clear()

    def set_algorithm(self, name):
        self.algorithm = name

    def get_data(self):
        with self.data_lock:
            if len(self.queue) > 0:
                return self.queue.pop()
            else:
                return None

    def put_data(self, finish=False):
        with self.run_lock:
            if not self.run:
                return 'close'
        with self.data_lock:
            if finish:
                self.queue.appendleft('finish')
            else:
                self.queue.appendleft(tuple(self.data))
            return True

    def sort(self, array):
        print(f'sort.py; sort; algorithm : {self.algorithm}')
        self.data = array.copy()
        self.run = True
        thr = threading.Thread(target=getattr(self, self.algorithm + '_sort'))
        thr.daemon = True
        thr.start()

    def bubble_sort(self):
        for i in range(len(self.data) - 1):
            for j in range(len(self.data) - i - 1):
                if self.data[j] > self.data[j + 1]:
                    self.data[j], self.data[j + 1] = self.data[j + 1], self.data[j]
                    if self.put_data() == 'close':
                        return 'close'

        self.put_data(finish=True)

    def quick_sort(self):
        def sort(low, high):
            if low < high:
                middle = partition(low, high)
                if sort(low, middle - 1) == 'close':
                    return 'close'
                if sort(middle, high) == 'close':
                    return 'close'

        def partition(low, high):
            a, b, c = self.data[low], self.data[(low + high) // 2], self.data[high]
            pivot = a + b + c - min(a, b, c) - max(a, b, c)  # changeable
            while low <= high:
                while self.data[low] < pivot:
                    low += 1
                while self.data[high] > pivot:
                    high -= 1
                if low <= high:
                    self.data[low], self.data[high] = self.data[high], self.data[low]
                    low, high = low + 1, high - 1
                    if self.put_data() == 'close':
                        return 'close'
            return low

        if sort(0, len(self.data) - 1) == 'close':
            return 'close'
        self.put_data(finish=True)

    def heap_sort(self):
        def heapify(head, tail):
            left = head * 2 + 1  # left_index+1 = right_index
            while left < tail:
                if left + 1 < tail and self.data[left] < self.data[left + 1]:
                    left += 1
                if self.data[left] <= self.data[head]:
                    break
                self.data[head], self.data[left] = self.data[left], self.data[head]
                head, left = left, left * 2 + 1
                if self.put_data() == 'close':
                    return 'close'

        for i in range(len(self.data) // 2 - 1, -1, -1):
            if heapify(i, len(self.data)) == 'close':
                return 'close'
        for i in range(len(self.data) - 1, 0, -1):
            self.data[i], self.data[0] = self.data[0], self.data[i]
            if self.put_data() == 'close':
                return 'close'
            if heapify(0, i) == 'close':
                return 'close'
        self.put_data(finish=True)

    def insertion_sort(self):
        for i in range(1, len(self.data)):
            for j in range(i, 0, -1):
                if self.data[j] < self.data[j - 1]:
                    self.data[j], self.data[j - 1] = self.data[j - 1], self.data[j]
                    if self.put_data() == 'close':
                        return 'close'
                else:
                    break
        self.put_data(finish=True)

    def merge_sort(self):  # TODO showing; in-place have problem
        def sort(arr):
            if len(arr) < 2:
                return
            middle = len(arr) // 2
            arr_1 = arr[0:middle]
            arr_2 = arr[middle:len(arr)]
            sort(arr_1)
            sort(arr_2)
            if merge(arr_1, arr_2, arr) == 'close':
                return 'close'

        def merge(arr_1, arr_2, arr):
            i, j = 0, 0
            while i + j < len(arr):
                if j == len(arr_2) or (i < len(arr_1) and arr_1[i] < arr_2[j]):
                    arr[i + j] = arr_1[i]
                    i += 1
                else:
                    arr[i + j] = arr_2[j]
                    j += 1
                if self.put_data() == 'close':
                    return 'close'

        if sort(self.data) == 'close':
            return 'close'
        self.put_data(finish=True)

    def gnome_sort(self):
        pos = 0
        while pos < len(self.data):
            if pos == 0 or self.data[pos] >= self.data[pos - 1]:
                pos += 1
            else:
                self.data[pos], self.data[pos - 1] = self.data[pos - 1], self.data[pos]
                if self.put_data() == 'close':
                    return 'close'
                pos -= 1
        self.put_data(finish=True)

    def bogo_sort(self):
        while True:
            flag = True
            for i in range(len(self.data) - 1):
                if self.data[i] > self.data[i + 1]:
                    flag = False
                    break
            if flag:
                break
            random.shuffle(self.data)
            if self.put_data() == 'close':
                return 'close'
        self.put_data(finish=True)

    def selection_sort(self):
        for i in range(0, len(self.data) - 1):
            min_id = i
            for j in range(i + 1, len(self.data)):
                if self.data[j] < self.data[min_id]:
                    min_id = j
            if min_id != i:
                self.data[i], self.data[min_id] = self.data[min_id], self.data[i]
                if self.put_data() == 'close':
                    return 'close'
        self.put_data(finish=True)

    def shell_sort(self):
        gap = 1
        while gap < len(self.data):  # Robert Sedgewick
            gap = gap*3+1
        gap = gap // 3
        while gap > 0:
            for i in range(gap):
                for j in range(i + gap, len(self.data), gap):
                    for k in range(j, gap-1, -gap):
                        if self.data[k] < self.data[k - gap]:
                            self.data[k], self.data[k - gap] = self.data[k - gap], self.data[k]
                            if self.put_data() == 'close':
                                return 'close'
                        else:
                            break
            gap = gap // 3
        self.put_data(finish=True)


'''    def radix_sort(self):
        # assume each data is natural number
        length = len(max(self.data))

        def classify(i):
            count = [0] * 10
            for x in self.data:
                count[int(str(x)[i]) % 10] += 1

        for i in range(length-1, -1, -1):
            classify(i)'''

'''if __name__ == '__main__':
    # ['bogo','merge', 'bubble', 'insertion', 'quick', 'selection', 'gnome', 'heap', 'shell'] 'merge', 'radix', 'comb'
    for x in ['bubble']:
        sorting = Sort()
        sorting.set_algorithm(x)
        data = [[13, 745, 35, 86, 24, 42, 123, 56, 75, 34, 7, 95, 53],
                [137, 7458, 355, 836, 24, 456, 34, 53, 245, 42, 19023, 568, 75, 346, 57, 78, 75, 795, 538]]
        for x in [data[0]]:
            arr = x.copy()
            sorting.sort(arr)
            if arr != sorted(x):
                print(arr, x)
        while len(sorting.queue):
            print(sorting.queue.pop())
    print('finish')
'''
