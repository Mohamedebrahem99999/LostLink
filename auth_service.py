from constants import *
from my_lib import *
from validation import Validation
import random
import time
from account import Account
from user_repository import UserRepository
from reset_password import ResetPassword

class AuthService:
    @classmethod
    def check_password(cls,id):
        """
        get the password from the user
        verifies email and allows user to reset his passowrd
        """

        users = UserRepository().get_all()

        for i in range(3):
            password = input("Please Enter your password: ")
            print("Checking Password...")
            time.sleep(1)
            
            if users[id].get("password") == password:
                print("\nLogin Successfully ✅✅")
                return True
            
            print("Wrong Password ❌❌")

            is_forgotten_input = input("Did you forgot your password?\n(enter 1 if yes 0 if no)")

            while is_forgotten_input not in ["0","1"]:
                print("Invalid Input")
                is_forgotten_input = input("Did you forgot your password?\n(enter 1 if yes 0 if no)")

            is_forgotten = is_forgotten_input == "1"
            
            if is_forgotten:
                reset_password = ResetPassword(users[id]["email"])
                if reset_password.verify_email(id):
                    return False
                    
            
            attempts_left = 3-(i+1)
            print("\n=====   Try again   =====")
            print(f"===== {attempts_left} attemps left =====\n")
        return False

    #=================================================================
    #===========================   Login   ===========================
    @classmethod
    def login(cls):
        users = UserRepository.get_all()
        email = Validation.get_email()

        found_user_id = -1
        for user_id in users:
            if users[user_id].get("email") == email:
                found_user_id = user_id  

        if found_user_id not in users:
            print("This email is not registered")
            print("You have to register first")
            return None
        if cls.check_password(found_user_id):
            user = users[found_user_id]
            
            if user.get("role") == "Manager":
                from Admin import Admin
                return Admin(
                    found_user_id,
                    user["name"],
                    user["email"],
                    user["password"],
                    phone=user["phone"],
                    age=user["age"],
                    gender=user["gender"],
                )

            return Account(
                found_user_id,
                user["name"],
                user["email"],
                user["password"],
                user["phone"],
                user["age"],
                user["gender"],
            )
        return None
    #==================================================================
    #==========================   Register   ==========================
    @classmethod
    def register(cls):
        """
        Register user data if doesn't have acc
        """
        users = UserRepository().get_all()

        email = Validation.get_email()
        for id in users:
            if users[id]["email"] == email:
                print("You already have account")
                return None
        password = Validation.get_password()
        name = input("Please Enter your name: ")
        phone = Validation.get_phone()
        gender = Validation.get_gender()
        age = Validation.get_age() 
        
        user_id = UserRepository.add_entry(
            {
                "name":name,
                "email":email,
                "password":password,
                "phone":phone,
                "age":age,
                "gender":gender,
                "role":"Member"
            }
        )   
        if user_id != -1:
            return Account(
                user_id,
                name,
                email,
                password,
                phone,
                age,
                gender,
            ) 
        else:
            return None

    @staticmethod
    def print_success_registeration():
        print("Registered Successfully✅✅")
        time.sleep(1)
        print("Redirecting to login gate..")
        time.sleep(1)

    @staticmethod
    def print_failure_registeration():
        print("Registeration Failed ❌❌")