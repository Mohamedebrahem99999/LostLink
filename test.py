from auth_service import AuthService
from 
from output import *
from input import *


def show_user_menu(member):
    while True:
        print_user_menu(member.get_name())
        choice = read_number_in_range("Select an option (1-9): ",9,1 )       
        if 
        if choice == 3:
            member.show_borrowed_items()
                
        elif choice == 4:
            print("\n___ Profile Information ___")
            print(member.display_profile())
            
        elif choice == 5:
            Account.edit_user_data(member.get_user_id())

        elif choice == 6:
            search_item()
        
        elif choice == 7:
            print("\n______ Borrow Item ______\n")
            print("_____ Available Items ______")
            # ItemRepository.show_available_items()
            item_id = Validation.get_id("Enter Item ID to borrow: ")
            # ItemRepository.borrow_item(user_id=member.get_user_id(), item_id=item_id)
      
        elif choice == 8:
          print("\n--- Return Item ---")
          member.show_borrowed_items()
          item_id = input("Enter Item ID to return: ").strip()
        #   ItemRepository.return_item(user_id=member.get_user_id(), item_id=item_id)
      
        elif choice == 9:
            print("Logged out successfully! 👋")
            break
        else:
            print("Invalid option. Please try again.")

def show_manager_menu(manager):
    while True:
        print_admin_menu(manager.get_name())
        choice = read_number_in_range("Select an option (1-15): ",15,1)
        if choice == 1:
            pass
            # ItemRepository.display_all_data(manager.get_role())

        if choice == 2:
            print()
            print("___ Available Items ___")
            print()
            # ItemRepository.show_available_items()
            
        elif choice == 3:
            print()
            print("___ Unvailable Items ___")
            print()
            # ItemRepository.show_unavailable_items(manager.get_role())

        elif choice == 4:
            print("\n___ Profile Information ___")
            print(manager.display_profile())

        elif choice == 5:
            UserRepository.display_all_data()

        elif choice == 6:
            Account.add_user()

        elif choice == 7:
            target_id = input("Enter User ID to delete: ").strip()
            UserRepository.remove_data(target_id)

        elif choice == 8:
            print("___ Edit User Data ___")
            target_id = Validation.get_id("Enter User ID to edit: ")
            Account.edit_user_data(target_id)

        elif choice == 9:
            add_new_item()
            
        elif choice == 10:
            item_id = input("Enter Item ID to delete: ").strip()
            # ItemRepository.remove_data(item_id)

        elif choice == 11:
            edit_item_data()

        elif choice == 12:
            pass
            # ItemRepository.show_available_items()
            # borrow_item()

        elif choice == 13:
            search_item()

        elif choice == 14:
            search_user()

        elif choice == 15:
            print("Logged out successfully! 👋")
            break
        else:
            print("Invalid option. Please try again.")

AuthService.login()