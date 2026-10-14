def show_edit_list(fields):
    for i, name in enumerate(fields, 1):
        print(f"{i}. edit {name}")
    print(f"{len(fields) + 1}. cancel")

def print_admin_menu(name):
    print("\n" + "=" * 40)
    print(f"Admin Menu (Welcome, {name})")
    print("_" * 40)
    print("1. Show All Items")
    print("2. Show Lost Items")
    print("3. Show Found Items")
    print("4. Show Profile")
    print("5. Show All Users Profile")
    print("6. Add User")
    print("7. Delete User")
    print("8. Edit User Data")
    print("9. Add Item")
    print("10. Delete Item")
    print("11. Edit Item Data")
    print("12. Search Item")
    print("13. Search User")
    print("14. Logout")
    print("_" * 40)

def print_user_menu(name):
    print("\n" + "=" * 40)
    print(f"User Menu (Welcome, {name})")
    print("=" * 40)
    print("1. Show All Items")
    print("2. Show Lost Items")
    print("3. Show Found Items")
    print("4. Show Profile")
    print("5. Edit Profile")
    print("6. Search Item")
    print("7. Add Lost Item")
    print("8. Add Found Item")
    print("9. Logout")
    print("=" * 40)
    
def print_goodbye_message():
    print("\nThank you for using the Digital Library System. Goodbye! 👋")

def print_welcome_message():
    print()
    print("_" * 10 + " Digital Library System " + "_" * 10)
    print()
    print("1. Login")
    print("2. Register")
    print("3. Exit System")
    print("_" * 45)
    print()

def print_page_message(pagename):
    print()
    print(f"{'_'*5} Welcome to {pagename} page {'_'*5}")
    print()