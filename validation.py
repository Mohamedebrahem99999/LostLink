from constants import *
import re
class Validation:

    @staticmethod
    def get_key(allowed_list,message = "Enter key\n"):
        while True:
            print("\n" + " ,".join(allowed_list) + "\n")
            key = input(message).strip()
            if key in allowed_list:
                return key
            print("Invalid Choice")
            
    @staticmethod
    def get_item_type(message = "choose a type  "):    
        message = message + "\nb (for book), mgz (for magazine) or  dr (for digital resource):"
        while True:
            item_type = input(message).lower()
            if item_type in ["b", "mgz", "dr"]:
                return item_type
            print("Invalid Input")

    @staticmethod
    def get_id(message):
        while True:
            id = input(message)
            if id.isdigit():
                return id
            print("Invalid Input, ID must be of digits only")

 
    @staticmethod
    def get_gender():
        print("Please Enter your gender:")
        print("1) Male")
        print("2) Female")
        print("3) Other")
        gender_input = input("").strip()
        gender_map = {"1": "male", "2": "female"}
        return gender_map.get(gender_input, "other")

    @staticmethod
    def get_phone(message = "Please Enter your phone: "):
        """
        get the right pone from the user by checking with an phone regex
        """
        while True:
            phone = input(message)
            if re.match(PHONE_REGEX, phone):
                return phone
            print("Invalid mobile phone")
    @staticmethod
    def get_age(message = "Enter your age: "):
        while True:
            age_input = input(message)
            if age_input.isdigit():
                return int(age_input)
            print("Invalid age, numbers only")

    @staticmethod
    def get_email():
        """
        get the right email from the user by checking with an email regex
        """
        while True:
            email = input("Please Enter your email: ")
            if re.match(Email_REGEX, email):
                return email
            print("Invalid email address")

    @staticmethod
    def get_password():
        while True:
            password = input("Enter a 6-character password: ")
            if len(password) >= 6:
                return password
            print("Too short")