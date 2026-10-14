import json
import os 

class DataRepository:
    _file_path = ""
    _data_dict = None

    @classmethod
    def get_all(cls):
        if cls._data_dict is not None:
            return cls._data_dict
        if (os.path.exists(cls._file_path) and os.path.getsize(cls._file_path) > 0):
            try:
                with open(cls._file_path, "r", encoding="utf-8") as file:
                    cls._data_dict = json.load(file)
            except json.JSONDecodeError:
                cls._data_dict = {}
        else:
            cls._data_dict = {}
        return cls._data_dict

    @classmethod
    def get_by_id(cls, record_id):
        data = cls.get_all()
        return data.get(str(record_id), {})

    @classmethod
    def save_data(cls):
        data = cls.get_all()
        with open(cls._file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

    @classmethod
    def generate_id(cls):
        all_data = cls.get_all()
        if all_data:
            return str(max(map(int, all_data.keys())) + 1)
        return "1"
    
    @classmethod
    def add_entry(cls, data):
        all_data = cls.get_all()
        new_id = cls.generate_id()
        all_data[new_id] = data
        cls.save_data()
        print("Data added successfully ✅")
        return new_id

    @classmethod
    def update_data(cls, data_id, data_key, new_data):
        all_data = cls.get_all()
        data_id = str(data_id)
        
        if data_id in all_data: 
            record = all_data[data_id]
            if data_key not in record:
                print("Error: Key not found in record.")
                return
            all_data[data_id][data_key] = new_data
            cls.save_data()
            print("Data updated successfully ✅")
        else:
            print(f"Error: Record with ID '{data_id}' not found.")

    @classmethod
    def remove_data(cls, record_id):
        record_id = str(record_id)
        data = cls.get_all()
        if record_id in data:
            assurance = input("Are you sure you want to delete this id [y/n]: ").strip().lower()
            if assurance == "y":
                del data[record_id]
                cls.save_data()
                print("Item deleted successfully! ✅")
            elif assurance == "n":
                return
            else:
                print("Invalid choice.")
        else:
            print("ID not found.")
    
    @classmethod
    def search(cls, search_key, value_wanted, role="Member"):
        data = cls.get_all()
        found = False
        for data_id, item in data.items():
            if str(item.get(search_key)).lower() == str(value_wanted).lower():
                cls.display_info(data_id, role)
                found = True
        if not found:
            print("No matching items found.")

    @classmethod
    def display_all_data(cls):
        data = cls.get_all()
        for data_id in data:
            cls.display_info(data_id)
        
    @classmethod
    def display_info(cls, record_id, role="Member"):
        pass