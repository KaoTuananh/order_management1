import json
import os
from typing import List, Optional, Callable, Any

from .customer import Customer, ShortCustomer, ValidationError
from .observer import Observable


class CustomerRepository(Observable):
    """Репозиторий клиентов с паттерном Наблюдатель."""

    def __init__(self, file_path: str = "customers.json"):
        super().__init__()
        self._file_path = file_path
        self._customers: List[Customer] = []
        self._next_id = 1
        self._load_data()

    def _load_data(self):
        """Загрузить данные из JSON файла."""
        if os.path.exists(self._file_path):
            try:
                with open(self._file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        try:
                            customer = Customer.from_dict(item)
                            self._customers.append(customer)
                        except ValidationError as e:
                            print(f"Ошибка валидации данных: {e}")
                            continue

                if self._customers:
                    self._next_id = max(c.customer_id for c in self._customers) + 1
            except Exception as e:
                print(f"Ошибка загрузки данных: {e}")
                self._customers = []
        else:
            self._customers = []

    def _save_data(self):
        """Сохранить данные в JSON файл."""
        try:
            # Создаем директорию, если она не существует
            os.makedirs(os.path.dirname(self._file_path), exist_ok=True)

            data = [customer.to_dict() for customer in self._customers]
            with open(self._file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            # Уведомляем наблюдателей об изменении
            self.notify_observers({"action": "save", "count": len(data)})
        except Exception as e:
            print(f"Ошибка сохранения данных: {e}")

    def get_all(self) -> List[Customer]:
        """Получить всех клиентов."""
        return self._customers.copy()

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        """Получить клиента по ID."""
        for customer in self._customers:
            if customer.customer_id == customer_id:
                return customer
        return None

    def add(self, customer_data: dict) -> bool:  # НОВЫЙ МЕТОД
        """Добавить клиента."""
        try:
            customer_id = self._next_id
            self._next_id += 1

            customer = Customer(
                customer_id=customer_id,
                name=customer_data.get('name', ''),
                address=customer_data.get('address', ''),
                phone=customer_data.get('phone', ''),
                contact_person=customer_data.get('contact_person', '')
            )

            self._customers.append(customer)
            self._save_data()
            self.notify_observers({
                "action": "add",
                "customer": customer,
                "customer_id": customer_id
            })
            return True
        except ValidationError as e:
            print(f"Ошибка валидации при добавлении: {e}")
            return False
        except Exception as e:
            print(f"Error adding customer: {e}")
            return False

    def get_k_n_short_list(self, k: int, n: int,
                           filter_func: Optional[Callable[[Customer], bool]] = None) -> List[ShortCustomer]:
        """Получить список с пагинацией."""
        filtered = self._customers
        if filter_func:
            filtered = [c for c in filtered if filter_func(c)]

        start = (k - 1) * n
        end = start + n
        paginated = filtered[start:end]

        return [ShortCustomer(c.customer_id, c.name, c.phone, c.contact_person) for c in paginated]

    def get_count(self, filter_func: Optional[Callable[[Customer], bool]] = None) -> int:
        """Получить количество клиентов."""
        if filter_func:
            return len([c for c in self._customers if filter_func(c)])
        return len(self._customers)