"""ReportIndex: look up an item by ID with hash / binary / linear search."""
from data_structures import HashTable , merge_sort , binary_search , linear_search
from text_utils import get_value


#==================================
#REPORT INDEX (look up an item by ID)
#==================================

class ReportIndex:
    # method "hash"  : O(1) average, uses HashTable
    # method "binary": O(log n), uses the list sorted by ID with merge_sort
    # method "linear": O(n), needs no preparation
    def __init__(self , items):
        self.skipped = []
        self.table = HashTable()
        self.unsorted_pairs = []
        for index , item in enumerate(items or []):
            item_id = None if item is None else get_value(item , "item_id")
            if not isinstance(item_id , str) or not item_id.strip():
                self.skipped.append({"index": index , "reason": "missing item ID"})
                continue
            item_id = item_id.strip().upper()
            if self.table.contains(item_id):
                self.skipped.append({"index": index , "item_id": item_id , "reason": "duplicate item ID"})
                continue
            self.table.put(item_id , item)
            self.unsorted_pairs.append((item_id , item))
        self.sorted_pairs = merge_sort(self.unsorted_pairs , lambda a , b: a[0] < b[0])

    def find_by_id(self , item_id , method = "hash"):
        # Returns (item or None , comparisons)
        target = str(item_id).strip().upper()
        first_of_pair = lambda pair: pair[0]
        if method == "hash":
            probes_before = self.table.probes
            return self.table.get(target) , self.table.probes - probes_before
        if method == "binary":
            position , probes = binary_search(self.sorted_pairs , target , first_of_pair , False)
            return (self.sorted_pairs[position][1] if position >= 0 else None) , probes
        if method == "linear":
            position , comparisons = linear_search(self.unsorted_pairs , target , first_of_pair)
            return (self.unsorted_pairs[position][1] if position >= 0 else None) , comparisons
        raise ValueError("method must be 'hash', 'binary' or 'linear'.")

    def __len__(self):
        return len(self.table)
 
