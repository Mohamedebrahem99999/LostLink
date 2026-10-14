"""Text / date helpers used by the matching system."""
from datetime import datetime , date
import re
from constants import DATE_PATTERN , STOPWORDS , KNOWN_COLORS , COLOR_ALIASES , SHADE_WORDS


#==================================
#HELPER FUNCTIONS
#==================================

def get_value(item , field):
    # Works for Item objects AND for dicts (item.to_dict())
    if isinstance(item , dict):
        return item.get(field)
    return getattr(item , field , None)

def get_report_type(item):
    # 1) the class: LostItem -> lost, FoundItem -> found (subclasses too)
    if not isinstance(item , dict):
        class_names = [cls.__name__ for cls in type(item).__mro__]
        if "LostItem" in class_names:
            return "lost"
        if "FoundItem" in class_names:
            return "found"
    # 2) an optional "report_type" key in a dict
    elif clean_text(item.get("report_type")) in ["lost" , "found"]:
        return clean_text(item.get("report_type"))
    # 3) the ID pattern of models.py: L### or F###
    first_letter = clean_text(get_value(item , "item_id"))[:1]
    return {"l": "lost" , "f": "found"}.get(first_letter)

def clean_text(value):
    # lower case, trim, one space between words. Anything that is not text -> ""
    if not isinstance(value , str):
        return ""
    return re.sub(r"\s+" , " " , value.strip().lower())

def remove_plural(word):
    # "keys" -> "key", but "glass" stays "glass"
    return word[:-1] if len(word) > 3 and word.endswith("s") and not word.endswith("ss") else word

def get_words(value):
    # Text -> SET of useful words (stop-words removed)
    words = set()
    for word in re.findall(r"[a-z0-9]+" , clean_text(value)):
        if word not in STOPWORDS and (len(word) > 1 or word.isdigit()):
            words.add(remove_plural(word))
    return words

def get_colors(value):
    # "Dark Navy and red" -> {"blue" , "red"}. Unknown color words are kept as they are.
    words = [COLOR_ALIASES.get(word , word) for word in re.findall(r"[a-z0-9]+" , clean_text(value))]
    known = set(word for word in words if word in KNOWN_COLORS)
    return known if known else set(word for word in words if word not in SHADE_WORDS)

def parse_date(value):
    # models.py keeps date as "YYYY-MM-DD" text until validate_date() runs. We accept both.
    # Missing or invalid date -> None (never crashes).
    if isinstance(value , datetime):
        return value.date()
    if isinstance(value , date):
        return value
    if not isinstance(value , str) or not re.fullmatch(DATE_PATTERN , value.strip()):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None

def to_plain(item):
    # Dict copy of the original item, safe to show in Streamlit
    if isinstance(item , dict):
        return dict(item)
    if hasattr(item , "to_dict"):
        try:
            return dict(item.to_dict())
        except Exception:
            pass
    return dict(vars(item)) if hasattr(item , "__dict__") else {"repr": repr(item)}
