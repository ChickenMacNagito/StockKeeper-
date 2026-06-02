import json
import os
from typing import List
from models import Item

DATA_FILE = 'data.json'


def save_data(items: List[Item]) -> bool:
    """Сохраняет список товаров в JSON-файл.

    Args:
        items: Список объектов Item.

    Returns:
        bool: True при успехе, False при ошибке.
    """
    try:
        data = [item.to_dict() for item in items]
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения: {e}")
        return False


def load_data() -> List[Item]:
    """Загружает товары из JSON-файла.

    Returns:
        List[Item]: Список товаров или пустой список при ошибке.
    """
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return [Item.from_dict(item) for item in data]
    except (json.JSONDecodeError, KeyError):
        print("Файл повреждён, создаём новый")
        return []
    


    
    