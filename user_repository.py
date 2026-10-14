from data_repository import DataRepository

class UserRepository(DataRepository):
    _file_path = "users.json"
    _data_dict = None

    @classmethod
    def get_info(cls, user_id):
        user = cls.get_by_id(user_id)
        if not user:
            return "User Not Found"
        return (
            f"ID = {user_id} | "
            f"name: {user.get('name')} | "
            f"email: {user.get('email')} | "
            f"password: {user.get('password')} | "
            f"phone: {user.get('phone')} | "
            f"age: {user.get('age')} | "
            f"gender: {user.get('gender')} | "
            f"borrowed items: {user.get('borrowed_items', []) or 'None'}"
        )
        
    @classmethod
    def display_info(cls, user_id):
        """To print user data"""
        print(cls.get_info(user_id))
    
    @classmethod
    def is_manager(cls, role):
        return role == "Manager" or role == "Admin"
    
    @classmethod
    def is_duplicated_email(cls, email):
        data = cls.get_all()
        for data_id in data:
            if data[data_id].get("email") == email:
                return True
        return False
    
    @classmethod
    def add_entry(cls, data):
        if cls.is_manager(data.get("role")):
            print("You Cannot Add Admin's/Manager's Data")
            return -1
        
        if "name" in data and "email" in data and "password" in data:
            if cls.is_duplicated_email(data.get("email")):
                print("Email is already registered")
                return -1
            data["phone"] = data.get("phone", "")
            data["age"] = data.get("age", 0)
            data["gender"] = data.get("gender", "")
            data["borrowed_items"] = data.get("borrowed_items", [])
            data["role"] = data.get("role", "Member")
            return super().add_entry(data)
        return -1
        
    @classmethod
    def update_data(cls, id, data_key, new_data):
        users = cls.get_all()
        user_id = str(id)
        if user_id in users: 
            user = users[user_id]
            if cls.is_manager(user.get("role")):
                print("You Cannot edit Admin's/Manager's data")
                return
            if data_key == "role":
                print("You Cannot update this key")
                return
            if data_key not in user:
                print("You cannot update unfound key")
                return
            users[user_id][data_key] = new_data
            cls.save_data()
            print("Data Updated Successfully ✅")
            return
        print("ID not Found")

    @classmethod
    def remove_data(cls, id):
        id = str(id)
        users = cls.get_all()
        if id in users:
            if cls.is_manager(users.get(id).get("role")):
                print("You cannot delete admin's/manager's data") 
                return
            name = users.get(id).get("name")
            super().remove_data(id)
            print(f"User {name} deleted successfully! ✅")
        else:
            print("User Not Found")

    @classmethod
    def search(cls, search_key, value_wanted):
        users = cls.get_all()
        found = False
        for user_id in users:
            user = users[user_id]
            try:
                val = user.get(search_key)
                if val and str(val).lower() == str(value_wanted).lower():
                    if cls.is_manager(user.get("role")):
                        continue
                    found = True
                    cls.display_info(user_id)
            except (AttributeError, SyntaxError):
                pass
        if not found:
            print("User Not Found")