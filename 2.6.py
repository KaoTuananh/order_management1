"""
Паттерн Адаптер для интеграции LegacyProductService.
Реализует пункт 6.
"""

import json
from typing import List, Optional, Dict, Any, Callable
from entities import Customer, ShortCustomer, ValidationError
from repository_base import CustomerRepBase, SortField


class LegacyProductService:
    """Старый сервис для работы с товарами (Adaptee)."""

    def __init__(self):
        """Инициализация сервиса с тестовыми данными."""
        self._products = [
            {"product_id": 101, "name": "Ноутбук", "price": 50000, "has_delivery": True},
            {"product_id": 102, "name": "Мышь", "price": 1500, "has_delivery": False},
            {"product_id": 103, "name": "Клавиатура", "price": 3500, "has_delivery": True},
            {"product_id": 104, "name": "Монитор", "price": 25000, "has_delivery": True},
        ]

    def fetch_product(self, code: int) -> Optional[Dict[str, Any]]:
        """
        Найти товар по коду.

        Args:
            code: код товара

        Returns:
            Словарь с данными товара или None
        """
        for product in self._products:
            if product["product_id"] == code:
                return product
        return None

    def add_product_entry(self, product_info: Dict[str, Any]) -> int:
        """
        Добавить запись о товаре.

        Args:
            product_info: информация о товаре

        Returns:
            ID нового товара
        """
        max_id = max([p["product_id"] for p in self._products], default=100)
        new_id = max_id + 1
        product_info["product_id"] = new_id
        self._products.append(product_info)
        return new_id

    def total_entries(self) -> int:
        """
        Получить общее количество товаров.

        Returns:
            Количество товаров
        """
        return len(self._products)

    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Получить все товары.

        Returns:
            Список всех товаров
        """
        return self._products.copy()


class Product:
    """Класс товара."""

    def __init__(
        self,
        product_id: int = 0,
        name: str = "",
        price: float = 0.0,
        has_delivery: bool = False,
    ):
        """
        Инициализация товара.

        Args:
            product_id: идентификатор товара
            name: название товара
            price: цена товара
            has_delivery: наличие доставки
        """
        self.product_id = product_id
        self.name = name
        self.price = price
        self.has_delivery = has_delivery

    def to_short_string(self) -> str:
        """Краткое строковое представление товара."""
        delivery = "с доставкой" if self.has_delivery else "без доставки"
        return f"ID: {self.product_id}, Товар: {self.name}, Цена: {self.price}, {delivery}"

    def __str__(self) -> str:
        """Строковое представление товара."""
        return f"Product(ID={self.product_id}, Name={self.name}, Price={self.price})"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "price": self.price,
            "has_delivery": self.has_delivery,
        }


class ProductShort:
    """Краткое представление товара."""

    def __init__(self, product_id: int, name: str, price: float):
        """
        Инициализация краткого представления товара.

        Args:
            product_id: идентификатор товара
            name: название товара
            price: цена товара
        """
        self.product_id = product_id
        self.name = name
        self.price = price

    def __str__(self) -> str:
        """Строковое представление."""
        return f"ID: {self.product_id}, Товар: {self.name}, Цена: {self.price}"


class ProductRepositoryAdapter(CustomerRepBase):
    """Адаптер для интеграции LegacyProductService в иерархию репозиториев."""

    def __init__(self):
        """Инициализация адаптера."""
        self._legacy_service = LegacyProductService()
        self._data_list: List[Customer] = []  # Используем Customer для совместимости
        self._load_from_service()

    def _load_from_service(self) -> None:
        """Загрузить данные из старого сервиса."""
        self._data_list = []
        for product_data in self._legacy_service.get_all_products():
            try:
                # Используем специальный телефон для товаров, который проходит валидацию
                phone = "+70000000000"  # Валидный телефон
                customer = Customer(
                    customer_id=product_data["product_id"],
                    name=product_data["name"],
                    address="Склад №1",  # Валидный адрес
                    phone=phone,
                    contact_person="Поставщик",
                )
                # Добавляем дополнительные атрибуты
                customer._price = product_data["price"]
                customer._has_delivery = product_data["has_delivery"]
                customer._is_product = True
                customer._product_phone = phone  # Сохраняем оригинальный телефон
                self._data_list.append(customer)
            except ValidationError as e:
                print(f"Ошибка валидации товара {product_data['name']}: {e}")
                continue

    def read_from_file(self) -> None:
        """Чтение данных из сервиса."""
        self._load_from_service()

    def write_to_file(self) -> None:
        """Для адаптера запись в файл не требуется."""
        pass

    def get_by_id(self, c_id: int) -> Optional[Customer]:
        """Получить товар по ID."""
        for customer in self._data_list:
            if customer.customer_id == c_id and hasattr(customer, "_is_product"):
                return customer
        return None

    def get_k_n_short_list(
        self,
        k: int,
        n: int,
        filter_func: Optional[Callable[[Customer], bool]] = None,
        sort_key: Optional[Callable[[Customer], Any]] = None,
        reverse: bool = False,
    ) -> List[ShortCustomer]:
        """Получить короткий список товаров."""
        # Фильтруем только товары
        product_data = [c for c in self._data_list if hasattr(c, "_is_product")]

        # Применяем фильтр
        if filter_func:
            product_data = [c for c in product_data if filter_func(c)]

        # Сортировка
        if sort_key:
            product_data.sort(key=sort_key, reverse=reverse)
        else:
            # Сортировка по ID по умолчанию
            product_data.sort(key=lambda x: x.customer_id)

        # Пагинация
        start = (k - 1) * n
        end = start + n
        paginated_data = product_data[start:end]

        # Преобразуем в ShortCustomer с информацией о товарах
        result = []
        for customer in paginated_data:
            price = getattr(customer, "_price", 0.0)
            # Используем специальный телефон для отображения
            phone = "Товар"
            result.append(
                ShortCustomer(
                    customer_id=customer.customer_id,
                    name=f"{customer.name} (${price})",
                    phone=phone,
                )
            )
        return result

    def add(self, new_customer: Customer) -> bool:
        """Добавить новый товар."""
        # Проверяем необходимые атрибуты
        if not hasattr(new_customer, "_price") or not hasattr(new_customer, "_has_delivery"):
            raise ValueError("Для добавления товара нужны атрибуты _price и _has_delivery")

        product_info = {
            "name": new_customer.name,
            "price": new_customer._price,
            "has_delivery": new_customer._has_delivery,
        }

        new_id = self._legacy_service.add_product_entry(product_info)

        # Обновляем customer для добавления в список
        new_customer.customer_id = new_id
        new_customer._is_product = True
        # Убедимся, что телефон валиден
        if not hasattr(new_customer, "_product_phone"):
            new_customer.phone = "+70000000000"
            new_customer._product_phone = new_customer.phone

        self._data_list.append(new_customer)
        return True

    def replace_by_id(self, c_id: int, new_customer: Customer) -> bool:
        """Заменить товар по ID."""
        for i, customer in enumerate(self._data_list):
            if customer.customer_id == c_id and hasattr(customer, "_is_product"):
                if not hasattr(new_customer, "_price") or not hasattr(new_customer, "_has_delivery"):
                    return False
                new_customer.customer_id = c_id
                new_customer._is_product = True
                # Убедимся, что телефон валиден
                if not hasattr(new_customer, "_product_phone"):
                    new_customer.phone = "+70000000000"
                    new_customer._product_phone = new_customer.phone
                self._data_list[i] = new_customer
                return True
        return False

    def delete_by_id(self, c_id: int) -> bool:
        """Удалить товар по ID."""
        for i, customer in enumerate(self._data_list):
            if customer.customer_id == c_id and hasattr(customer, "_is_product"):
                del self._data_list[i]
                # Также удалить из legacy service
                self._legacy_service._products = [
                    p for p in self._legacy_service._products if p["product_id"] != c_id
                ]
                return True
        return False

    def sort_by_field(self, field: SortField, reverse: bool = False) -> None:
        """Сортировка товаров по полю."""
        # В этом адаптере сортировка по полям Customer
        field_mapping = {
            SortField.CUSTOMER_ID: lambda x: x.customer_id,
            SortField.NAME: lambda x: x.name.lower(),
        }

        if field not in field_mapping:
            raise ValueError(f"Поле {field} недоступно для сортировки в адаптере")

        self._data_list.sort(key=field_mapping[field], reverse=reverse)

    def get_count(
        self, filter_func: Optional[Callable[[Customer], bool]] = None
    ) -> int:
        """Получить количество товаров."""
        product_data = [c for c in self._data_list if hasattr(c, "_is_product")]
        if filter_func:
            return len([c for c in product_data if filter_func(c)])
        return len(product_data)

    def get_all(self) -> List[Customer]:
        """Получить все товары."""
        return [c for c in self._data_list if hasattr(c, "_is_product")]