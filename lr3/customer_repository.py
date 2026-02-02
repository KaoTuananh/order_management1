from enum import Enum
from typing import List, Optional, Callable, Any, Dict

from .customer import Customer, ShortCustomer, ValidationError
from .observer import Observable, Observer


# ИСПОЛЬЗОВАНИЕ КЛАССА ИЗ ПРЕДЫДУЩЕЙ ЛР
class SortField(Enum):
    """Поля для сортировки."""
    CUSTOMER_ID = "customer_id"
    NAME = "name"
    ADDRESS = "address"
    PHONE = "phone"
    CONTACT_PERSON = "contact_person"


class CustomerRepository(Observable):
    """Репозиторий клиентов с паттерном Наблюдатель."""

    def sort_by_field(self, field: SortField, reverse: bool = False):
        """Сортировка по полю - ИСПОЛЬЗОВАНИЕ ИЗ ПРЕДЫДУЩЕЙ ЛР."""
        try:
            if field == SortField.NAME:
                self._customers.sort(key=lambda x: x.name.lower(), reverse=reverse)
            elif field == SortField.CUSTOMER_ID:
                self._customers.sort(key=lambda x: x.customer_id, reverse=reverse)
            elif field == SortField.PHONE:
                self._customers.sort(key=lambda x: x.phone, reverse=reverse)
            elif field == SortField.ADDRESS:
                self._customers.sort(key=lambda x: x.address.lower(), reverse=reverse)
            elif field == SortField.CONTACT_PERSON:
                self._customers.sort(key=lambda x: x.contact_person.lower(), reverse=reverse)

            self._save_data()
            self.notify_observers({"action": "sort", "field": field.value, "reverse": reverse})
        except Exception as e:
            print(f"Ошибка при сортировке: {e}")

    def get_k_n_short_list(self, k: int, n: int,
                           filter_func: Optional[Callable[[Customer], bool]] = None,
                           sort_by: Optional[str] = None,
                           reverse: bool = False) -> List[ShortCustomer]:
        """Получить список с пагинацией - ИСПОЛЬЗОВАНИЕ СОРТИРОВКИ ИЗ ПРЕДЫДУЩЕЙ ЛР."""
        filtered = self._customers
        if filter_func:
            filtered = [c for c in filtered if filter_func(c)]

        # Сортировка - ИСПОЛЬЗОВАНИЕ ЛОГИКИ ИЗ ПРЕДЫДУЩЕЙ ЛР
        if sort_by:
            if sort_by == 'customer_id':
                filtered.sort(key=lambda x: x.customer_id, reverse=reverse)
            elif sort_by == 'name':
                filtered.sort(key=lambda x: x.name.lower(), reverse=reverse)
            elif sort_by == 'address':
                filtered.sort(key=lambda x: x.address.lower(), reverse=reverse)
            elif sort_by == 'phone':
                filtered.sort(key=lambda x: x.phone, reverse=reverse)
            elif sort_by == 'contact_person':
                filtered.sort(key=lambda x: x.contact_person.lower(), reverse=reverse)

        start = (k - 1) * n
        end = start + n
        paginated = filtered[start:end]

        return [ShortCustomer(c.customer_id, c.name, c.phone, c.contact_person) for c in paginated]