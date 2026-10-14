import json
from user_repository import UserRepository
from data_repository import DataRepository

class ItemRepository(DataRepository):
    _file_path = "items.json"
    _data_dict = None

    @classmethod
    def display_all_data(cls, role="Member"):
        items = cls.get_all()
        if not items:
            print("No items found.")
            return
        for data_id in items:
            cls.display_info(data_id)
            print("-" * 40)
            
    @classmethod
    def display_info(cls, item_id):
        item = cls.get_by_id(item_id)
        if not item:
            print(f"Item with ID {item_id} not found.")
            return

        keywords = ", ".join(item.get("keywords", [])) if isinstance(item.get("keywords"), list) else item.get("keywords")

        print(
            f"ID: {item_id} | "
            f"Name: {item.get('name')} \n"
            f"Category: {item.get('category')} | "
            f"Color: {item.get('color')} \n"
            f"Location: {item.get('location')} | "
            f"Date: {item.get('date')} \n"
            f"Description: {item.get('description')} \n"
            f"Keywords: {keywords} \n"
            f"Related User: {item.get('related_user')} | "
            f"Report Type: {item.get('report_type')} | "
            f"Is Open: {item.get('is_open')}"
        )

    @classmethod
    def show_lost_items(cls):
        items = cls.get_all()
        lost_items = {k: v for k, v in items.items() if v.get("report_type") == "lost"}
        
        if not lost_items:
            print("No lost items reported.")
            return
            
        print("--- Lost Items ---")
        for item_id in lost_items:
            cls.display_info(item_id)
            print("-" * 30)

    @classmethod
    def show_found_items(cls):
        items = cls.get_all()
        found_items = {k: v for k, v in items.items() if v.get("report_type") == "found"}
        
        if not found_items:
            print("No found items reported.")
            return
            
        print("--- Found Items ---")
        for item_id in found_items:
            cls.display_info(item_id)
            print("-" * 30)

    @classmethod
    def mark_as_lost(cls, item_id):
        items = cls.get_all()
        if item_id in items:
            items[item_id]["is_open"] = True
            items[item_id]["report_type"] = "lost"
            cls.save_data()
            print(f"Item {item_id} marked as Lost.")
        else:
            print("Item not found.")
        
    @classmethod
    def mark_as_found(cls, item_id):
        items = cls.get_all()
        if item_id in items:
            items[item_id]["report_type"] = "found"
            cls.save_data()
            print(f"Item {item_id} marked as Found.")
        else:
            print("Item not found.")

    @classmethod
    def close_report(cls, item_id):
        items = cls.get_all()
        if item_id in items:
            items[item_id]["is_open"] = False
            cls.save_data()
            print(f"Report for item {item_id} has been closed.")
            return True
        else:
            print("Item not found.")
            return False

from item_repository import ItemRepository

print("=== 1. Display All Items ===")
ItemRepository.display_all_data()
print()
print("\n=== 2. Show Only Lost Items ===")
ItemRepository.show_lost_items()
print()
print("\n=== 3. Show Only Found Items ===")
ItemRepository.show_found_items()
print()
print("\n=== 4. Test Closing a Report (ID: 1) ===")
ItemRepository.close_report("1")
print()
print("\n=== 5. Test Changing Status to Lost (ID: 2) ===")
ItemRepository.mark_as_lost("2")
print()
print("\n=== 6. Display Specific Item Info (ID: 1) ===")
ItemRepository.display_info("1")
print()