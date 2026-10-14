from datetime import datetime , date
import re
from multiprocessing.spawn import old_main_modules

ID_PATTERN = r"^[LF]\d{3}$"
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"


#======================================
#CUSTOM EXCEPTIONS
#======================================

class InvalidItemError(Exception):
    pass

class EmptyFieldError(Exception):
    pass

class InvalidIDError(Exception):
    pass

class InvalidDateError(Exception):
    pass

class UnknownCategoryError(Exception):
    pass

class InvalidStatusError(Exception):
    pass

class InvalidLocationError(Exception):
    pass

class InvalidDescriptionError(Exception):
    pass

class InvalidColorError(Exception):
    pass

class MissingFieldError(Exception):
    pass


#==================================
#THE MAIN PROGRAM
#==================================
VALID_STATUSES = ["open", "matched", "claimed", "closed"]
CATEGORIES = ["phone" , "wallet" , "keys" , "bag" , "document" , "electronics" , "clothing" , "other"]
class Item:
    def __init__(self , item_id , category , color , location , date , description , status = "open"):
        self.item_id = item_id
        self.category = category
        self.color = color
        self.location = location
        self.date = date
        self.description = description
        self.status = status

    def to_dict(self):
        return{
            "item_id": self.item_id,
            "category":self.category,
            "color": self.color,
            "location": self.location,
            "date": self.date,
            "description": self.description,
            "status": self.status
        }
    @classmethod
    def from_dict(cls , data):
        required = ["item_id" , "category" , "color" , "location" , "date" , "description" , "status"]
        for key in required:
            if key not in data:
                raise MissingFieldError()
        return cls(
            data["item_id"] , data["category"] , data["color"] ,
            data["location"] , data["date"] , data["description"] ,
            data.get["status" , "open"]

        )
    def since_day(self):
        return (date.today() - self.date).days

    def validate_id(self):
        if not isinstance(self.item_id, str):
            raise InvalidIDError("ID must be string.")

        cleaned_id = self.item_id.strip().upper()

        if not re.fullmatch(ID_PATTERN, cleaned_id):
            raise InvalidIDError("try to enter a valid ID.")

        self.item_id = cleaned_id

        return self.item_id

    def validate_category(self):
        if not isinstance(self.category , str):
            raise UnknownCategoryError("category must be a string.")
        cleaned_category = self.category.strip()
        if not cleaned_category:
            raise UnknownCategoryError("category cannot be empty.")

        if cleaned_category not in CATEGORIES:
            available =",".join(sorted(CATEGORIES))
        raise UnknownCategoryError()

    def validate_color(self):
        if not isinstance(self.color , str):
            raise InvalidColorError("Color must be a string.")
        cleaned_color = self.color.strip()

        if not cleaned_color:
            raise InvalidColorError("Color cannot be empty.")

        cleaned_color = self.color.strip()
        return self.color

    def validate_location(self):
        if not isinstance(self.location, str):
            raise InvalidLocationError("Location must be a string.")

        cleaned_location = self.location.strip()

        if not cleaned_location:
            raise InvalidLocationError("Location cannot be empty.")

        if len(cleaned_location) < 3:
            raise InvalidItemError()

        if len(cleaned_location) > 100:
            raise InvalidLocationError(
                "Location must contain at most 100 characters."
            )

        cleaned_location = re.sub(r"\s+", " ", cleaned_location)

        self.location = cleaned_location
        return self.location

    def validate_date(self):
            if not isinstance(self.date, str):
                raise InvalidDateError("Date must be string.")

            cleaned_date = self.date.strip()
            if not re.fullmatch(DATE_PATTERN, cleaned_date):
                raise InvalidDateError("Date must use the format YYYY-MM-DD")
            try:
                parsed_date = date.fromisoformat(cleaned_date)
            except ValueError:
                raise InvalidDateError("Date must be a real number.")
            if parsed_date > date.today():
                raise InvalidDateError("Date cannot be in the future.")

            self.date = parsed_date
            return self.date


    def validate_description(self):
        if not isinstance(self.description, str):
            raise InvalidDescriptionError("Description must be a string.")

        cleaned_description = self.description.strip()
        if not cleaned_description:
            raise InvalidDescriptionError("Description cannot be empty.")

        if len(cleaned_description) < 5:
            raise ValueError(
                "Description must contain at least 5 characters."
            )

        if len(cleaned_description) > 300:
            raise InvalidDescriptionError(
                "Description must contain at most 300 characters."
            )

        cleaned_description = re.sub(
            r"\s+",
            " ",
            cleaned_description,
        )
        self.description = cleaned_description
        return self.description

    def validate_status(self):
        if not isinstance(self.status, str):
            raise InvalidStatusError("Status must be a string.")

        cleaned_status = self.status.strip().lower()

        if not cleaned_status:
            raise InvalidStatusError("Status cannot be empty.")

        if cleaned_status.lower() not in VALID_STATUSES:
            raise InvalidStatusError("Invalid status.")

        self.status = cleaned_status
        return self.status

    def is_matchable(self, other):
        if not isinstance(other, Item):
            return False
        if type(self) is type(other):
            return False

        if self.status.strip().lower() != "open":
            return False
        if other.status.strip().lower() != "open":
            return False

        my_category = self.category.strip().lower()
        other_category = other.category.strip().lower()

        return my_category == other_category and my_category in CATEGORIES



#==================================
#INHERTANCE CLASSES
#==================================

class LostItem(Item):
    def __init__(self, item_id, category, color, location, date, description, owner_name, reward, status="open"):
        super().__init__(item_id, category, color, location, date, description, status)
        self.owner_name = owner_name
        self.reward = reward

    def validate_owner_name(self):
        if not isinstance(self.owner_name , str) or None :
            raise InvalidItemError("Enter a valid owner name.")

        cleaned_owner_name = self.owner_name.strip()
        if not cleaned_owner_name:
            raise MissingFieldError("Owner name cannot be empty.")
        return self.owner_name


    def validate_reward(self):
        if not isinstance(self.reward , str) or None:
            raise InvalidItemError("Enter a valid reward.")

        cleaned_reward = self.reward.strip()
        if not cleaned_reward:
            raise MissingFieldError("Reward cannot be empty.")
        return self.reward

    def update_lost_details(self, **changes):
        if self.status.strip().lower() != "open":
            raise InvalidStatusError("Only open items can be updated.")

        if not changes:
            raise MissingFieldError("Nothing to update.")

        validators = {
            "color": self.validate_color,
            "location": self.validate_location,
            "description": self.validate_description,
            "owner_name": self.validate_owner_name,
            "reward": self.validate_reward,
        }

        unknown = set(changes) - set(validators)
        if unknown:
            raise InvalidItemError(
                "Cannot update: " + ", ".join(sorted(unknown))
            )
        old_values = {field: getattr(self, field) for field in changes}

        try:
            for field, value in changes.items():
                setattr(self, field, value)
                validators[field]()
        except Exception:
            for field, value in old_values.items():
                setattr(self, field, value)
            raise
        return self

class FoundItem(Item):
    def __init__(self, item_id, category, color, location, date, description, storage_location , found_condition, status="open"):
        super().__init__(item_id, category, color, location, date, description, status)
        self.storage_location = storage_location
        self.found_condition = found_condition

    def validate_storage_location(self):
        if not isinstance(self.storage_location , str) or None :
            raise InvalidLocationError("Enter a valid storage location.")

        cleaned_storage_location = self.storage_location.strip()
        if not cleaned_storage_location:
            raise InvalidLocationError("Storage location cannot be empty.")

        if len(cleaned_storage_location) < 3:
            raise InvalidLocationError("Storage location must contain at least 3 characters.")
        if len(cleaned_storage_location) > 100:
            raise InvalidLocationError("Storage location must contain at most 100 characters.")

        cleaned_location = re.sub(r"\s+", " ", cleaned_storage_location)

        self.location = cleaned_storage_location
        return self.storage_location

    def validate_found_condition(self):
        if not isinstance(self.found_condition , str) or None :
            raise InvalidItemError("Enter a valid condition.")

        cleaned_found_condition = self.found_condition.strip()
        if not cleaned_found_condition:
            raise MissingFieldError("Condition cannot be empty.")

        self.found_condition = cleaned_found_condition
        return self.found_condition

    def add_finding_location(self , specific_location):
        old_location = self.location
        self.location = specific_location

        try:
            self.validate_location()
        except Exception:
            self.location = old_location
            raise
        return self.location