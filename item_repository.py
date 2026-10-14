import json
from user_repository import UserRepository
from data_repository import DataRepository
class ItemRepository(DataRepository):
    _file_path = "items.json"
    _data_dict = None
    @classmethod
    def display_all_data(cls,role = "Member"):
        items = cls.get_all()
        for data_id in items:
            cls.display_info(data_id,role)
            
    @classmethod
    def display_info(cls,item_id,role = "Member"):
        """To return item Data"""

        item = cls.get_by_id(item_id)
        if not item:
            return
        borrowed_info = ""
        if not item.get('is_available') and item.get('borrowed_by') and role == "Manager":
            user_details = UserRepository.get_info(item['borrowed_by'])
            borrowed_info = f"\nBorrowed By:\n  {user_details}"

        print (
        f"ID = {item_id} | " +
        f"Category: {item['category']} | " +
        f"title: {item['title']} | " +
        (f"Author: {item.get('author')}" if item.get('author','') else '') + ' | ' +
        (f"ISBN: {item.get('isbn')} | " if item.get('isbn','') else '') +
        (f"issue number: {item.get('issue_number')} | " if item.get('issue_number','') else '') +
        (f"Publisher: {item.get('publisher')} | " if item.get('publisher','') else '') +
        (f"file format: {item.get('file_format')} | " if item.get('file_format','') else '') +
        (f"download_url: {item.get('download_url')} | " if item.get('download_url','') else '') +
        f"Item Type: {item.get('type','')} | "+
        f"Status: "
        f"{'available' if item['is_available'] 
           else 'unavailable'}" 
        f"{borrowed_info}"
        )

    @classmethod
    def show_available_items(cls):
        cls.search("is_available",True)

    @classmethod
    def show_unavailable_items(cls,role = "Member"):
        cls.search("is_available",False,role)

    @classmethod
    def borrow_item(cls,user_id,item_id):
        items = cls.get_all()
        users = UserRepository.get_all()
        
        if item_id not in items and user_id not in users:
            print("Item and User are Not Found")
        
        elif item_id not in items:
            print("Item Not Found")
            
        elif user_id not in users:
           print("User Not found")
    
        else:
            if UserRepository.is_manager(users.get(user_id).get("role")):
                print("A manager can not borrow items")
            else:
                if item_id in users.get(user_id).get('borrowed_items'):
                    print("You are already borrowing this item")
                    return
                if items[item_id]["is_available"]:
                    users[user_id]["borrowed_items"].append(item_id)
                    cls.mark_borrowed(item_id)
                    items[item_id]["borrowed_by"] = user_id
                    UserRepository.save_data()
                    cls.save_data()
                    print("Item Borrorwed Successfully ✅✅")
                    return True
                else:
                    print("This item is un available")
                    return False
        
    @classmethod
    def return_item(cls,user_id,item_id):
        items = cls.get_all()
        users = UserRepository.get_all()

        if item_id not in items and user_id not in users:
            print("Item and user are Not found")
            return None
        
        elif item_id not in items:
            print("Item Not Found")
            return None
        
        elif user_id not in users:
            print("User Not found")
            return None
        user_borrowed_books = users[user_id]["borrowed_items"]
        if item_id in items:
            if not items[item_id]["is_available"]:
    
                if item_id in user_borrowed_books:  
                    users[user_id]["borrowed_items"].remove(item_id)
                    cls.mark_returned(item_id)
                    items[item_id]["borrowed_by"] = ""
                    UserRepository.save_data()
                    cls.save_data()
                    return items[item_id]
    
                else:
                    print("This user never borrowed this item")
            else:
                print("This item is already unborrowed")
        else:
            print("This item does not exits")
            
        return None
    @classmethod
    def borrow_rule(cls):
        return "Standard 14-day borrowing period"
    
    @classmethod
    def mark_borrowed(cls,item_id):
        items = cls.get_all()
        if item_id in items:
            items[item_id]["is_available"] = False
        
    @classmethod
    def mark_returned(cls,item_id):
        items = cls.get_all()
        items[item_id]["is_available"] = True
    