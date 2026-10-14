import random
from user_repository import UserRepository
from constants import *
from account import Account
# from magazine import Magazine
# from digital_resource import DigitalResource
from my_lib import *
from validation import Validation
from input import *
        
def read_amount(prompt):
    while True:
        amount = input(prompt)
        if amount.isdigit() and float(amount) > 0:
            return float(amount)
        print("Negative amount is not acceptable")

def read_currency():
    while True:
        currency = input("Enter the currency (EGP, USD, SAR): ").upper()
        if currency in ["EGP", "USD", "SAR"]:
            return currency
        print("Invalid currency. Please enter EGP, USD, or SAR.")
    
def exchange_currency(currency, amount):
    if currency == "USD":
        return amount * 30
    elif currency == "SAR":
        return amount * 9
    return amount

def generate_rand_code(from_num, to_num):
    return random.randint(from_num, to_num)

def check_equality(first, second):
    return first == second

def search_item():
    item_type = Validation.get_item_type("Enter the item type you want to search for: ")
    user_search_keys = {
        "b": ["title", "author", "category", "isbn"],
        "mgz": ["title", "publisher", "issue_number"],
        "dr": ["title", "category", "file_format", "download_url"],
    }

    key = Validation.get_key(user_search_keys[item_type], "Enter a key to search by: ")
    value = input("Enter the value to search for: ")
    # ItemRepository.search(key, value)

def add_new_item():
    print("\n___ Add New Item ___")
    item_type = Validation.get_item_type()

    if item_type == "b":
        pass
        # Book.add_book()

    elif item_type == "mgz":
        pass
        # Magazine.add_magazine()

    elif item_type == "dr":
        pass
        # DigitalResource.add_digital_resource()

def edit_item_data():
    print("\n___ Edit Item Data ___")
    data_id = Validation.get_id("Enter Item ID to edit: ")
    # item_type = ItemRepository.get_by_id(data_id).get("type")

def search_user():
    user_search_keys = ["name", "email", "phone"]
    key = Validation.get_key(user_search_keys, "Enter a key to search by: ")
    value = input("Enter the value to search for: ")
    UserRepository.search(key, value)