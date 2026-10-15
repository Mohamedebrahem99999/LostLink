import re
from constants import *

class Validation:

    @staticmethod
    def get_key(allowed_list, message="Enter key\n"):
        while True:
            print("\nAllowed keys: " + ", ".join(allowed_list))
            key = input(message).strip().lower()
            if key in [item.lower() for item in allowed_list]:
                return key
            print("Invalid Choice. Please choose from the available keys.")
            
    @staticmethod
    def get_item_type(message="Choose a type"):    
        full_message = f"{message}\nb (for book), mgz (for magazine), or dr (for digital resource): "
        while True:
            item_type = input(full_message).strip().lower()
            if item_type in ["b", "mgz", "dr"]:
                return item_type
            print("Invalid Input. Please enter 'b', 'mgz', or 'dr'.")

    @staticmethod
    def get_id(message="Enter ID: "):
        while True:
            user_id = input(message).strip()
            if user_id.isdigit():
                return user_id
            print("Invalid Input, ID must contain digits only.")

    @staticmethod
    def get_gender():
        print("\nPlease Enter your gender:")
        print("1) Male")
        print("2) Female")
        print("3) Other")
        gender_input = input("Choose (1-3): ").strip()
        gender_map = {"1": "male", "2": "female"}
        return gender_map.get(gender_input, "other")

    @staticmethod
    def get_phone(message="Please enter your phone: "):
        """Get a valid phone number using phone regex."""
        while True:
            phone = input(message).strip()
            # التأكد من مطابقة الـ Regex المعرف في constants.py
            if re.match(PHONE_REGEX, phone):
                return phone
            print("Invalid mobile phone number. Please try again.")

    @staticmethod
    def get_age(message="Enter your age: "):
        while True:
            age_input = input(message).strip()
            if age_input.isdigit():
                age = int(age_input)
                if 0 < age < 120:  # إضافة تحقق منطقي للعمر
                    return age
                print("Please enter a realistic age.")
            else:
                print("Invalid age, numbers only.")

    @staticmethod
    def get_email():
        """Get a valid email using email regex."""
        while True:
            email = input("Please enter your email: ").strip()
            # استخدام Email_REGEX أو EMAIL_REGEX حسب المعرف في constants
            regex_pattern = globals().get("Email_REGEX") or globals().get("EMAIL_REGEX", r"^[\w\.-]+@[\w\.-]+\.\w+$")
            if re.match(regex_pattern, email):
                return email
            print("Invalid email address format.")

    @staticmethod
    def get_password(message="Enter a 6-character password: "):
        while True:
            password = input(message)
            if len(password) >= 6:
                return password
            print("Password is too short. It must be at least 6 characters.")

    @staticmethod
    def check_report_type(report_type):
        return report_type in ["lost", "found"]

    @staticmethod
    def check_report_date(date):
        from datetime import datetime
        try:
            datetime.strptime(date, "%Y-%m-%d")
            return True

        except (ValueError, TypeError):
            return False

    @staticmethod
    def check_required_fields(item):
        required_fields = [
            "name",
            "category",
            "location",
            "date",
            "report_type"
        ]

        return all(

            isinstance(item.get(field), str) and bool(item.get(field).strip())

            for field in required_fields
        )

    @staticmethod
    def check_color(color):
        return isinstance(color, str) and bool(color.strip())