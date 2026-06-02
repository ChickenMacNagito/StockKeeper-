import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..')))

from src.models import Item
from src.storage import save_data, load_data, DATA_FILE


def test_save_and_load():
    """Тест: сохранение и загрузка товаров."""
    items = [
        Item('Клавиатура', 5, 1500.0),
        Item('Мышь', 10, 450.0)
    ]

    assert save_data(items), "❌ Ошибка сохранения"
    loaded = load_data()

    assert len(loaded) == 2, "❌ Неверное количество товаров"
    assert loaded[0].name == 'Клавиатура', "❌ Ошибка в данных"

    # Очистка тестового файла
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)

    print("✅ Тесты пройдены!")


if __name__ == '__main__':
    test_save_and_load()
    