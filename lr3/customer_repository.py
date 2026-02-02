from typing import List, Optional, Callable, Any, Dict
from enum import Enum

from .customer import Customer, ShortCustomer, ValidationError
from .observer import Observable, Observer


class SortField(Enum):
    """Поля для сортировки."""
    CUSTOMER_ID = "customer_id"
    NAME = "name"
    ADDRESS = "address"
    PHONE = "phone"
    CONTACT_PERSON = "contact_person"


class CustomerRepository(Observable):
    """Репозиторий клиентов с паттерном Наблюдатель."""

    def get_k_n_short_list(self, k: int, n: int,
                           filter_func: Optional[Callable[[Customer], bool]] = None,
                           sort_by: Optional[str] = None,
                           reverse: bool = False) -> List[ShortCustomer]:
        """Получить список с пагинацией - ИСПОЛЬЗОВАНИЕ ФИЛЬТРАЦИИ ИЗ ПРЕДЫДУЩЕЙ ЛР."""
        filtered = self._customers
        if filter_func:
            filtered = [c for c in filtered if filter_func(c)]

        # Сортировка
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

    def get_count(self, filter_func: Optional[Callable[[Customer], bool]] = None) -> int:
        """Получить количество клиентов - ИСПОЛЬЗОВАНИЕ ФИЛЬТРАЦИИ ИЗ ПРЕДЫДУЩЕЙ ЛР."""
        if filter_func:
            return len([c for c in self._customers if filter_func(c)])
        return len(self._customers)