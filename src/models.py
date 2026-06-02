
class Item:
    """Класс товара с полями: название, количество, цена."""

    def __init__(self, name: str, quantity: int, price: float):
        """Инициализация товара."""
        self.name = name
        self.quantity = quantity
        self.price = price

    def to_dict(self) -> dict:
        """Конвертация объекта в словарь для JSON."""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Item':
        """Создание объекта Item из словаря."""
        return cls(
            name=data['name'],
            quantity=int(data['quantity']),
            price=float(data['price'])
        )

    def __repr__(self):
        """Строковое представление для отладки."""
        return f"Item('{self.name}', {self.quantity}, {self.price})"
    