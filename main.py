import time
from auth_service import AuthService
from my_lib import *
from input import *
def main():
    is_running = True
    while is_running:
        print_welcome_message()
        choice = read_number_in_range("Enter a choice between(1-3): ",3,1)
        if choice == 1:
            print_page_message("login")
            user = AuthService.login()
            if user:
                if user.get_role() == "Manager":
                    show_manager_menu(user)
                else:
                    show_member_menu(user)
                    
        elif choice == 2:
            print_page_message("Register")
            print("Registering...")
            time.sleep(1)
            if AuthService.register():                
                AuthService.print_success_registeration()
            else:
                AuthService.print_failure_registeration()

        elif choice == 3:
            print_goodbye_message()
            is_running = False
            
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()