"""Data structures and algorithms written from scratch:
HashTable, linear_search, binary_search, merge_sort.

Big-O: linear_search O(n) | binary_search O(log n) | merge_sort O(n log n)
       HashTable get/put O(1) average
"""
from matching_errors import UnsortedDataError


#==================================
#HASH TABLE (written from scratch)
#==================================
# djb2 hash + separate chaining. Capacity doubles when load factor > 0.75.

class HashTable:
    def __init__(self , capacity = 16):
        if not isinstance(capacity , int) or capacity < 1:
            raise ValueError("capacity must be a positive integer.")
        self.buckets = [[] for _ in range(capacity)]
        self.size = 0
        self.collisions = 0     # new key landed in a bucket that was not empty
        self.probes = 0         # key comparisons made by get / contains

    @staticmethod
    def hash_string(text):
        hash_value = 5381
        for character in text:
            hash_value = (hash_value * 33 + ord(character)) & 0xFFFFFFFF
        return hash_value

    def find_bucket(self , key):
        return self.buckets[self.hash_string(str(key)) % len(self.buckets)]

    def put(self , key , value):
        bucket = self.find_bucket(key)
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value         # key exists -> update
                return
        if bucket:
            self.collisions += 1
        bucket.append([key , value])
        self.size += 1
        if self.size / len(self.buckets) > 0.75:
            self.resize()

    def get(self , key , default = None):
        for pair in self.find_bucket(key):
            self.probes += 1
            if pair[0] == key:
                return pair[1]
        return default

    def contains(self , key):
        sentinel = object()
        return self.get(key , sentinel) is not sentinel

    def resize(self):
        old_buckets = self.buckets
        self.buckets = [[] for _ in range(len(old_buckets) * 2)]
        for bucket in old_buckets:
            for key , value in bucket:
                self.find_bucket(key).append([key , value])

    def __len__(self):
        return self.size


#==================================
#SEARCHING AND SORTING
#==================================

def linear_search(items , target , key = lambda x: x):
    # Works on unsorted data. Returns (index or -1 , comparisons). O(n)
    for index , item in enumerate(items):
        if key(item) == target:
            return index , index + 1
    return -1 , len(items)

def is_sorted(items , key = lambda x: x):
    return all(key(items[index - 1]) <= key(items[index]) for index in range(1 , len(items)))

def binary_search(sorted_items , target , key = lambda x: x , verify_sorted = True):
    # ONLY for data sorted from small to big. Returns (index or -1 , probes). O(log n)
    try:
        if verify_sorted and not is_sorted(sorted_items , key):
            raise UnsortedDataError("Binary search needs sorted data.")
        low , high , probes = 0 , len(sorted_items) - 1 , 0
        while low <= high:
            middle = (low + high) // 2
            probes += 1
            middle_key = key(sorted_items[middle])
            if middle_key == target:
                return middle , probes
            if middle_key < target:
                low = middle + 1
            else:
                high = middle - 1
        return -1 , probes
    except TypeError:
        raise UnsortedDataError("Keys cannot be compared with each other.")

class SortStats:
    def __init__(self):
        self.comparisons = 0
        self.swaps = 0              # elements copied into the merged list
        self.recursive_calls = 0

def merge_sort(items , precedes , stats = None):
    # precedes(a , b) must return True when a goes STRICTLY before b.
    # Stable, O(n log n), does not change the original list.
    if stats is None:
        stats = SortStats()
    stats.recursive_calls += 1
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle] , precedes , stats)
    right = merge_sort(items[middle:] , precedes , stats)

    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        stats.comparisons += 1
        stats.swaps += 1
        if precedes(right[j] , left[i]):    # take from the right only if strictly earlier
            merged.append(right[j])
            j += 1
        else:
            merged.append(left[i])
            i += 1
    stats.swaps += (len(left) - i) + (len(right) - j)
    return merged + left[i:] + right[j:]
