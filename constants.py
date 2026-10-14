import os
MAX_ATTEMPTS = 3
PASSWORD = ""
if os.path.exists("password.txt") and os.path.getsize("password.txt") > 0:
    with open("password.txt", "r") as pass_file:
        PASSWORD = pass_file.readline().strip()

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDEREMAIL = "mohammedebrahem99999@gmail.com"
Email_REGEX = r"^[a-zA-Z0-9.]+@gmail\.com$"
PHONE_REGEX = r"^01[0125]\d{8}$"
ISBN_PATTERN = r"^[\d-]{10,17}$"
URL_REGEX = r"^https?://[^\s/$.?#].[^\s]*/.+\.(PDF|DOCX|DOC|PPTX|TXT|EPUB|RTF)(\?[^\s]*)?$"
ALLOWED_FILE_FORMAT = ['PDF', 'DOCX', 'DOC', 'PPTX', 'TXT', 'EPUB', 'RTF']


#==================================
#LOSTLINK MATCHING CONSTANTS
#==================================
CATEGORIES = ["phone" , "wallet" , "keys" , "bag" , "document" , "electronics" , "clothing" , "other"]
VALID_STATUSES = ["open" , "matched" , "claimed" , "closed"]
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"
MATCHABLE_STATUS = "open"       # models.is_matchable() only accepts "open" items

# Category is a GATE (same rule as is_matchable), so it is not scored. Weights add up to 100.
DEFAULT_WEIGHTS = {"color": 30.0 , "location": 30.0 , "date": 20.0 , "description": 20.0}
ATTRIBUTES = ["color" , "location" , "date" , "description"]
DISCLAIMER = ("This is only a suggestion based on matching details. "
              "It is not proof of ownership; staff must verify before returning any item.")

STOPWORDS = set("a an the and or of in on at to with near for is it this that my was were has have had very some".split())
KNOWN_COLORS = set("black white gray red blue green yellow orange purple pink brown beige".split())
COLOR_ALIASES = {"grey": "gray" , "silver": "gray" , "navy": "blue" , "violet": "purple" , "maroon": "red" ,
                 "crimson": "red" , "gold": "yellow" , "tan": "beige" , "cream": "beige" , "khaki": "beige" ,
                 "turquoise": "blue"}
SHADE_WORDS = set(["dark" , "light" , "bright" , "pale" , "deep" , "and" , "with"])
RELATED_COLORS = [("black" , "gray") , ("white" , "gray") , ("white" , "beige") , ("red" , "pink") ,
                  ("red" , "orange") , ("brown" , "beige") , ("brown" , "orange") , ("blue" , "purple") ,
                  ("yellow" , "orange")]
