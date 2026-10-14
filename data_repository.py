import json
import os 

class DataRepository:
    _file_path = ""
    _data_dict = None

    @classmethod
    def get_all(cls):
        if cls._data_dict is not None:
            return cls._data_dict
        if ( os.path.exists(cls._file_path)
            and os.path.getsize(cls._file_path) > 0):
            try:
                with open(
                    cls._file_path,
                    "r",
                    encoding="utf-8") as users_file:
                    cls._data_dict = json.load(users_file)
            except json.JSONDecodeError:
                cls._data_dict = {}
        else:
            cls._data_dict = {}
        return cls._data_dict

    @classmethod
    def get_by_id(cls,id):
        users = cls.get_all()
        return users.get(str(id),{})

    @classmethod
    def save_data(cls):
        users = cls.get_all()
        with open(cls._file_path,
                  "w",
                  encoding="utf-8") as users_file:
            json.dump(users,users_file,indent=4)

    @classmethod
    def generate_id(cls):
        all_data = cls.get_all()
        id = "0"
        if all_data:
            id = str(max(map(int,all_data.keys())) + 1)
        else:
            id = "1"
        return id
    
    @classmethod
    def add_entry(cls,data):
        """add new items to the json files"""
        all_data = cls.get_all()
        new_id = cls.generate_id()
        all_data[new_id] = data
        cls.save_data()
        print("Data added Successfully ✅")
        return new_id

    @classmethod
    def update_data(cls,data_id,data_key,new_data):
        users = cls.get_all()
        data_id = str(data_id)
        
        if data_id in users: 
            user = users[data_id]
            if data_key not in user:
                print("You can not update unfound key")
                return
            users[data_id][data_key] = new_data
            cls.save_data()
            print("Data Updated Successfully✅")
        else:
            print(("Error: Record with ID "
                   f"'{data_id}' not found."))

    @classmethod
    def remove_data(cls,id):
        id = str(id)
        data = cls.get_all()
        if id in data:
            assurance = input("Are you sure you want to delete this id[y/n]: ").lower()
            if assurance == "y":
                del data[id]
                cls.save_data() 
            elif assurance == "n":
                return
            else:
                print("Invalid Choice")
                return
            print("Item deleted successfully! ✅")
        else:
            print("ID Not Found")
    
    @classmethod
    def search(cls,search_key,value_wanted,role = "Member"):
        data = cls.get_all()
        found = False
        for data_id in data:
            item = data[data_id]
            if str(item.get(search_key)).lower() == str(value_wanted).lower():
                cls.display_info(data_id,role)
                found = True
        if not found:
            print("No Found Items")

    @classmethod
    def display_all_data(cls):
        data = cls.get_all()
        for data_id in data:
            cls.display_info(data_id)
        
    @classmethod
    def display_info(cls,id,role = "Member"):
        pass