import json
import os
from collections import deque
from typing import Dict, Any, List, Optional

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(BASE_DIR, 'items.json')

class DataManager:
    def __init__(self, file_path: str = DATA_FILE_PATH):
        self.file_path = file_path
        self.items_dict: Dict[str, Dict[str, Any]] = {}
        self.history_stack = deque()
        self.processing_queue = deque()
        self.load_data()

    def load_data(self):
        if not os.path.isfile(self.file_path):
            raise FileNotFoundError(f'Item database not found: {self.file_path}')
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError('items.json must contain an object keyed by item ID')
        if any(not isinstance(v, dict) for v in data.values()):
            raise ValueError('Every item must be a JSON object')
        self.items_dict = {str(k): v for k, v in data.items()}
        return self.items_dict

    def save_data(self) -> bool:
        directory = os.path.dirname(os.path.abspath(self.file_path))
        os.makedirs(directory, exist_ok=True)
        temp_path = self.file_path + '.tmp'
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(self.items_dict, f, ensure_ascii=False, indent=4)
            os.replace(temp_path, self.file_path)
            return True
        except OSError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def add_item(self, item_dict: Dict[str, Any]) -> bool:
        if not isinstance(item_dict, dict):
            raise TypeError('Item must be a dictionary')
        item = item_dict.copy()
        raw_id = item.pop('item_id', None)
        item_id = str(raw_id).strip() if raw_id is not None else str(max([int(k) for k in self.items_dict if k.isdigit()], default=0) + 1)
        if not item_id:
            raise ValueError('Item ID cannot be empty')
        if item_id in self.items_dict:
            raise ValueError(f'Item ID {item_id} already exists')
        if 'is_open' not in item:
            item['is_open'] = item.get('status', 'open') == 'open'
        item.pop('status', None)
        self.items_dict[item_id] = item
        try:
            self.save_data()
        except OSError:
            del self.items_dict[item_id]
            raise
        self.processing_queue.append(item_id)
        self.history_stack.append({'action': 'ADD', 'item_id': item_id, 'previous_state': None})
        return True

    def get_all_items(self) -> List[Dict[str, Any]]:
        return list(self.items_dict.values())

    def get_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        return self.items_dict.get(str(item_id))

    def delete_item(self, item_id: str) -> bool:
        item_id = str(item_id)
        if item_id not in self.items_dict:
            return False
        previous = self.items_dict.pop(item_id)
        try:
            self.save_data()
        except OSError:
            self.items_dict[item_id] = previous
            raise
        self.processing_queue = deque(k for k in self.processing_queue if k != item_id)
        self.history_stack.append({'action': 'DELETE', 'item_id': item_id, 'previous_state': previous})
        return True

    def undo_last_action(self) -> bool:
        if not self.history_stack:
            return False
        action = self.history_stack[-1]
        item_id = action['item_id']
        before = self.items_dict.get(item_id)
        if action['action'] == 'ADD':
            self.items_dict.pop(item_id, None)
        elif action['action'] == 'DELETE':
            self.items_dict[item_id] = action['previous_state']
        try:
            self.save_data()
        except OSError:
            if before is None:
                self.items_dict.pop(item_id, None)
            else:
                self.items_dict[item_id] = before
            raise
        self.history_stack.pop()
        return True
