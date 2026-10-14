"""Scoring: PreparedReport (clean copy of an item), MatchConfig, similarity functions,
eligibility check and the final 0-100 score.  Score one pair = O(k)."""
from constants import MATCHABLE_STATUS , DEFAULT_WEIGHTS , ATTRIBUTES , RELATED_COLORS
from matching_errors import InvalidMatchItemError , InvalidConfigError
from text_utils import get_value , get_report_type , clean_text , get_words , get_colors , parse_date


#==================================
#PREPARED REPORT (clean copy used for comparing)
#==================================

class PreparedReport:
    def __init__(self , item):
        if item is None or isinstance(item , (str , bytes , int , float , bool , list , tuple , set)):
            raise InvalidMatchItemError("Item must be an Item object or a dict.")

        item_id = get_value(item , "item_id")
        # same cleaning as validate_id()
        self.item_id = item_id.strip().upper() if isinstance(item_id , str) and item_id.strip() else None

        status = get_value(item , "status")
        if status is None or (isinstance(status , str) and not status.strip()):
            self.status = MATCHABLE_STATUS          # models.py default is "open"
        else:
            self.status = clean_text(status) or "invalid"

        self.report_type = get_report_type(item)
        self.category = clean_text(get_value(item , "category"))
        self.colors = get_colors(get_value(item , "color"))
        self.location_text = clean_text(get_value(item , "location"))
        self.location_words = get_words(get_value(item , "location"))
        self.when = parse_date(get_value(item , "date"))
        self.description_words = get_words(get_value(item , "description"))
        self.original = item


#==================================
#SCORING
#==================================

class MatchConfig:
    # weights          : partial dict merged onto DEFAULT_WEIGHTS (0 switches an attribute off)
    # date_window_days : date similarity goes from 1 (same day) down to 0 over this many days
    # date_grace_days  : a found item may be dated this many days BEFORE the lost item
    # partial_threshold: similarity from this value up to 1 is "partial", below it "mismatch"
    # Missing data always earns 0 points, so a sparse report cannot look perfect.
    def __init__(self , weights = None , date_window_days = 14 , date_grace_days = 0 ,
                 partial_threshold = 0.4 , strong_score = 75 , possible_score = 50):
        self.weights = dict(DEFAULT_WEIGHTS)
        self.weights.update(weights or {})
        self.date_window_days = date_window_days
        self.date_grace_days = date_grace_days
        self.partial_threshold = partial_threshold
        self.strong_score = strong_score
        self.possible_score = possible_score
        self.validate()

    def validate(self):
        for name , weight in self.weights.items():
            if name not in ATTRIBUTES:
                raise InvalidConfigError("Unknown weight: " + str(name))
            if isinstance(weight , bool) or not isinstance(weight , (int , float)) or weight != weight or weight < 0:
                raise InvalidConfigError("Weight for " + name + " must be a number >= 0.")
        if sum(self.weights.values()) <= 0:
            raise InvalidConfigError("At least one weight must be greater than 0.")
        if not isinstance(self.date_window_days , int) or self.date_window_days < 1 or \
                not isinstance(self.date_grace_days , int) or self.date_grace_days < 0:
            raise InvalidConfigError("date_window_days must be 1 or more and date_grace_days cannot be negative.")
        if not 0 < self.partial_threshold <= 1 or not 0 <= self.possible_score <= self.strong_score <= 100:
            raise InvalidConfigError("Check partial_threshold (0-1) and possible_score <= strong_score <= 100.")

def jaccard(first , second):
    union = first | second
    return len(first & second) / len(union) if union else 0.0      # no division by zero


# Each function returns (similarity from 0 to 1 , detail text). Similarity is None when data is missing.

def color_similarity(lost , found):
    if not lost.colors or not found.colors:
        return None , "color missing on one or both items"
    if lost.colors == found.colors:
        return 1.0 , "same color (" + ", ".join(sorted(lost.colors)) + ")"
    if lost.colors & found.colors:
        return jaccard(lost.colors , found.colors) , "shared color: " + ", ".join(sorted(lost.colors & found.colors))
    for first in lost.colors:
        for second in found.colors:
            if (first , second) in RELATED_COLORS or (second , first) in RELATED_COLORS:
                return 0.5 , "related colors"
    return 0.0 , "different colors"

def location_similarity(lost , found):
    if not lost.location_words or not found.location_words:
        return None , "location missing on one or both items"
    if lost.location_text == found.location_text:
        return 1.0 , "same location '" + found.location_text + "'"
    shared = lost.location_words & found.location_words
    if not shared:
        return 0.0 , "different locations"
    similarity = jaccard(lost.location_words , found.location_words)
    # "library" inside "main library" is a strong partial match
    if lost.location_words <= found.location_words or found.location_words <= lost.location_words:
        similarity = max(similarity , 0.8)
    return similarity , "shared location words: " + ", ".join(sorted(shared))

def date_similarity(lost , found , config):
    if lost.when is None or found.when is None:
        return None , "date missing or invalid on one or both items"
    gap = abs((found.when - lost.when).days)
    return max(0.0 , 1.0 - gap / config.date_window_days) , "found " + str(gap) + " day(s) from the lost date"

def description_similarity(lost , found):
    if not lost.description_words or not found.description_words:
        return None , "description missing on one or both items"
    shared = lost.description_words & found.description_words
    return jaccard(lost.description_words , found.description_words) , \
        "shared words: " + (", ".join(sorted(shared)) if shared else "none")

def check_eligibility(lost , found , config):
    # Same rules as Item.is_matchable() in models.py, plus a date check.
    # Returns (True , "") or (False , reason)
    if lost.report_type != "lost":
        return False , "first item is not a lost item"
    if found.report_type != "found":
        return False , "second item is not a found item"
    if lost.status != MATCHABLE_STATUS or found.status != MATCHABLE_STATUS:
        return False , "status is not open"
    if not lost.category or not found.category:
        return False , "category missing"
    if lost.category != found.category:
        return False , "different category"
    if lost.when and found.when and (found.when - lost.when).days < -config.date_grace_days:
        return False , "found date is earlier than the lost date"
    return True , ""

def compute_score(lost , found , config):
    # Returns (score from 0 to 100 , breakdown rows). One row per attribute:
    # points = similarity * weight / total weight * 100, so the rows add up to the score.
    similarities = {"color": color_similarity(lost , found) ,
                    "location": location_similarity(lost , found) ,
                    "date": date_similarity(lost , found , config) ,
                    "description": description_similarity(lost , found)}
    active = [name for name in ATTRIBUTES if config.weights.get(name , 0) > 0]
    total_weight = sum(config.weights[name] for name in active)

    rows = []
    score = 0.0
    for name in active:
        similarity , detail = similarities[name]
        max_points = config.weights[name] / total_weight * 100
        points = 0.0 if similarity is None else similarity * max_points
        if similarity is None:
            status = "missing"
        elif similarity >= 1.0:
            status = "matched"
        elif similarity >= config.partial_threshold:
            status = "partial"
        else:
            status = "mismatch"
        score += points
        rows.append({"attribute": name , "status": status ,
                     "similarity": None if similarity is None else round(similarity , 3) ,
                     "max_points": round(max_points , 2) , "points": round(points , 2) , "detail": detail})
    return round(max(0.0 , min(100.0 , score)) , 2) , rows


#==================================
#LABEL AND SUMMARY
#==================================

def get_label(score , config):
    if score >= config.strong_score:
        return "Strong suggestion"
    return "Possible suggestion" if score >= config.possible_score else "Weak suggestion"

def build_summary(score , label , rows):
    def names(status):
        return ", ".join(row["attribute"] for row in rows if row["status"] == status) or "none"
    return ("Score " + format(score , ".1f") + "/100 (" + label + "). Same category (required). "
            "Matched: " + names("matched") + ". Partial: " + names("partial") + ". "
            "Different: " + names("mismatch") + ". Missing: " + names("missing") + ". "
            "Review manually - not proof of ownership.")
