# ==========================================
# LostLink System Import Aggregator
# (my_imports.py)
# ==========================================

# 1. System Constants
from constants import (
    MAX_ATTEMPTS, PASSWORD, SMTP_SERVER, SMTP_PORT, SENDEREMAIL,
    Email_REGEX, PHONE_REGEX, ISBN_PATTERN, URL_REGEX, ALLOWED_FILE_FORMAT,
    CATEGORIES, VALID_STATUSES, DATE_PATTERN, MATCHABLE_STATUS,
    DEFAULT_WEIGHTS, ATTRIBUTES, DISCLAIMER, STOPWORDS, KNOWN_COLORS,
    COLOR_ALIASES, SHADE_WORDS, RELATED_COLORS
)

# 2. Exceptions & Errors
from matching_errors import (
    MatchingError, InvalidMatchItemError, InvalidReportTypeError,
    InvalidThresholdError, InvalidConfigError, UnsortedDataError
)
from models import (
    InvalidItemError, EmptyFieldError, InvalidIDError, InvalidDateError,
    UnknownCategoryError, InvalidStatusError, InvalidLocationError,
    InvalidDescriptionError, InvalidColorError, MissingFieldError
)

# 3. Core Models
from models import Item, LostItem, FoundItem

# 4. Data Structures & Algorithms
from data_structures import (
    HashTable, linear_search, is_sorted, binary_search, SortStats, merge_sort
)

# 5. Text & Date Utilities
from text_utils import (
    get_value, get_report_type, clean_text, remove_plural,
    get_words, get_colors, parse_date, to_plain
)

# 6. Scoring System
from scoring import (
    PreparedReport, MatchConfig, check_eligibility, compute_score,
    get_label, build_summary
)

# 7. Matching Engine & Report Index
from report_index import ReportIndex
from matching_engine import (
    MatchingEngine, DEFAULT_ENGINE, find_matches, find_matches_detailed
)