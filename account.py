import json
import os
from user import Account
from validation import Validation
# from my_lib import *
from input import *
from output import *
from user_repository import UserRepository
# from item_repository import ItemRepository

# =================================================================
# ====================  Subclass 1: Member  =======================
# =================================================================
class Account(Account):

  def __init__(
      self,
      user_id,
      name,
      email,
      password,
      phone="",
      age=0,
      gender="",
      borrowed_items=None,
  ):
    
    super().__init__(
        user_id =user_id,
        name = name,
        email = email,
        password = password,
        phone = phone,
        age = age,
        gender = gender,
        role = "Member"
    )
    self._borrowed_items = borrowed_items or []
    self._role = "Member"

  def display_profile(self):
    base_info = super().display_profile()
    return f"{base_info} | Borrowed Items: {len(self._borrowed_items)}"

  def show_borrowed_items(self):

    print("\n___ Borrowed Items ___")
    users_data = UserRepository.get_all()
    user_info = users_data.get(self.get_user_id(), {})
    borrowed_ids = user_info.get("borrowed_items", [])
    if borrowed_ids:
        for item_id in borrowed_ids:
            ItemRepository.display_info(item_id)
    else:
        print("No borrowed items found.")

  @staticmethod
  def edit_user_data(user_id):
    edit_list = ["name", "phone", "age", "password", "cancel"]
    show_edit_list(edit_list)
    en_edit_list = dict(enumerate(edit_list))

    choice = read_number_in_range("Select what to update (1-5): ", 5,1)
    new_data = None
    if choice == 1:
        new_data = input("Enter new name: ").strip()
    elif choice == 2:
        new_data = Validation.get_phone()
    elif choice == 3:
        new_data = Validation.get_age()
    elif choice == 4:
        new_data = Validation.get_password()
    elif choice == 5:
        return
    else:
        print("Invalid choice.")
        return 
    UserRepository.update_data(user_id, en_edit_list[choice-1], new_data)
    