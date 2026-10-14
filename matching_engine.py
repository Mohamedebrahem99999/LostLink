'''matching_engine.py  (LostLink - Person 2)
 Suggests which FOUND items may belong to a LOST item.
 A match is only a SUGGESTION. It is never proof of ownership.

 Works with Person 1's models.py: LostItem / FoundItem objects (or dicts made by to_dict()).
 The report type comes from the class (LostItem -> "lost", FoundItem -> "found").

 Big-O (n = found items, m = matches kept, k = words per text)
   score one pair O(k)       find_matches O(n*k + m log m)    merge_sort O(n log n)
   linear_search O(n)        binary_search O(log n)           HashTable get/put O(1) average

 Module map:  constants.py (settings) | matching_errors.py (exceptions) | text_utils.py (cleaning)
              data_structures.py (HashTable, search, sort) | scoring.py (score one pair)
              matching_engine.py (this file: ranking + find_matches) | report_index.py (lookup by ID)'''
from constants import MATCHABLE_STATUS , DISCLAIMER
from matching_errors import InvalidMatchItemError , InvalidReportTypeError , InvalidThresholdError
from data_structures import HashTable , SortStats , merge_sort
from scoring import PreparedReport , MatchConfig , check_eligibility , compute_score , get_label , build_summary
from text_utils import to_plain

# Re-exports: old code that did "from matching_engine import HashTable / ReportIndex / ..." keeps working.
from matching_errors import MatchingError , InvalidConfigError , UnsortedDataError            # noqa: F401
from data_structures import linear_search , binary_search , is_sorted                         # noqa: F401
from report_index import ReportIndex                                                          # noqa: F401


#==================================
#ENGINE
#==================================

def result_comes_first(first , second):
    # Ranking rule: higher score first. Tie -> newer found date. Tie -> smaller ID.
    if first["score"] != second["score"]:
        return first["score"] > second["score"]
    if first["found_date"] != second["found_date"]:
        if first["found_date"] is None or second["found_date"] is None:
            return second["found_date"] is None
        return first["found_date"] > second["found_date"]
    return first["found_id"] < second["found_id"]

def check_threshold(threshold):
    if isinstance(threshold , bool) or not isinstance(threshold , (int , float)) \
            or threshold != threshold or threshold < 0 or threshold > 100:
        raise InvalidThresholdError("Threshold must be a number between 0 and 100.")
    return float(threshold)

class MatchingEngine:
    def __init__(self , config = None):
        self.config = config if config is not None else MatchConfig()

    def find_matches_detailed(self , lost_item , found_items , threshold = 0 , top_n = None):
        config = self.config
        threshold = check_threshold(threshold)
        if top_n is not None and (isinstance(top_n , bool) or not isinstance(top_n , int) or top_n < 1):
            raise InvalidMatchItemError("top_n must be a positive whole number or None.")

        lost = PreparedReport(lost_item)
        if lost.report_type != "lost":
            raise InvalidReportTypeError("Search needs a LostItem (lost report).")

        if found_items is None:
            found_items = []
        if isinstance(found_items , (str , bytes , dict)) or not hasattr(found_items , "__iter__"):
            raise InvalidMatchItemError("found_items must be a list of found items.")
        found_items = list(found_items)

        skipped = []                    # data problems (bad item, missing ID, duplicate ...)
        stats = {"total_input": len(found_items) , "scored": 0 , "not_eligible": 0 ,
                 "not_eligible_reasons": {} , "below_threshold": 0 , "returned": 0}
        if lost.status != MATCHABLE_STATUS:
            stats["note"] = "The lost item is not open, so nothing was compared."
            return {"lost_id": lost.item_id , "matches": [] , "skipped": skipped ,
                    "stats": stats , "disclaimer": DISCLAIMER}

        seen_ids = HashTable()          # O(1) duplicate detection
        results = []
        for index , raw_item in enumerate(found_items):
            try:
                found = PreparedReport(raw_item)
            except InvalidMatchItemError as error:
                skipped.append({"index": index , "item_id": None , "reason": str(error)})
                continue
            problem = None
            if found.item_id is None:
                problem = "missing item ID"
            elif found.report_type != "found":
                problem = "not a found item (type: " + str(found.report_type) + ")"
            elif seen_ids.contains(found.item_id):
                problem = "duplicate item ID"
            if problem:
                skipped.append({"index": index , "item_id": found.item_id , "reason": problem})
                continue
            seen_ids.put(found.item_id , True)

            eligible , reason = check_eligibility(lost , found , config)
            if not eligible:
                stats["not_eligible"] += 1
                stats["not_eligible_reasons"][reason] = stats["not_eligible_reasons"].get(reason , 0) + 1
                continue

            score , rows = compute_score(lost , found , config)
            stats["scored"] += 1
            if score < threshold:
                stats["below_threshold"] += 1
                continue
            label = get_label(score , config)
            results.append({"rank": 0 , "lost_id": lost.item_id , "found_id": found.item_id ,
                            "score": score , "label": label , "is_tie": False ,
                            "summary": build_summary(score , label , rows) , "breakdown": rows ,
                            "found_date": found.when , "item": to_plain(raw_item) ,
                            "disclaimer": DISCLAIMER})

        sort_stats = SortStats()
        ranked = merge_sort(results , result_comes_first , sort_stats)
        for position , result in enumerate(ranked):
            result["rank"] = position + 1
            same_as_before = position > 0 and ranked[position - 1]["score"] == result["score"]
            same_as_next = position + 1 < len(ranked) and ranked[position + 1]["score"] == result["score"]
            result["is_tie"] = same_as_before or same_as_next
            result["found_date"] = result["found_date"].isoformat() if result["found_date"] else None
        ranked = ranked[:top_n] if top_n is not None else ranked

        stats["returned"] = len(ranked)
        stats["sort"] = dict(vars(sort_stats))
        return {"lost_id": lost.item_id , "matches": ranked , "skipped": skipped ,
                "stats": stats , "disclaimer": DISCLAIMER}


DEFAULT_ENGINE = MatchingEngine()

def find_matches(lost_item , found_items , threshold = 0 , top_n = None , config = None):
    # MAIN FUNCTION FOR THE UI.
    # lost_item: one LostItem (or dict) | found_items: list of FoundItem objects (or dicts), None gives []
    # threshold: minimum score 0-100 (included)
    # Returns a list of dicts, best first: rank, lost_id, found_id, score, label, is_tie,
    # summary, breakdown, found_date, item, disclaimer
    return find_matches_detailed(lost_item , found_items , threshold , top_n , config)["matches"]

def find_matches_detailed(lost_item , found_items , threshold = 0 , top_n = None , config = None):
    # Same as find_matches but returns a dict that also has "skipped" (with reasons) and "stats"
    engine = DEFAULT_ENGINE if config is None else MatchingEngine(config)
    return engine.find_matches_detailed(lost_item , found_items , threshold , top_n)
