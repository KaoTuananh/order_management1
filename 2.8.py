"""
Декоратор для файловых репозиториев с фильтрацией и сортировкой.
Реализует пункт 8.
"""

import re
from typing import List, Optional, Dict, Any, Callable
from repository_base import CustomerRepBase
from entities import Customer, ShortCustomer


class FileRepositoryDecorator(CustomerRepBase):
    """
    Декоратор для файловых репозиториев (JSON/YAML).
    Реализует фильтрацию и сортировку для методов работы с файлами.
    """

    def __init__(self, repository: CustomerRepBase):
        """
        Инициализация декоратора.

        Args:
            repository: декорируемый репозиторий
        """
        self._repository = repository
        self._filter_functions: List[Callable[[Customer], bool]] = []
        self._sort_key: Optional[Callable[[Customer], Any]] = None
        self._reverse = False

    def read_from_file(self) -> None:
        """Делегировать чтение из файла."""
        return self._repository.read_from_file()

    def write_to_file(self) -> None:
        """Делегировать запись в файл."""
        return self._repository.write_to_file()

    def get_by_id(self, c_id: int) -> Optional[Customer]:
        """Делегировать поиск по ID."""
        return self._repository.get_by_id(c_id)

    def get_k_n_short_list(
        self,
        k: int,
        n: int,
        filter_func: Optional[Callable[[Customer], bool]] = None,
        sort_key: Optional[Callable[[Customer], Any]] = None,
        reverse: bool = False,
    ) -> List[ShortCustomer]:
        """Делегировать получение списка с пагинацией."""
        # Объединяем фильтры
        combined_filter = self._combine_filters(filter_func)

        # Используем переданную сортировку или дефолтную
        actual_sort_key = sort_key if sort_key is not None else self._sort_key
        actual_reverse = reverse if sort_key is not None else self._reverse

        return self._repository.get_k_n_short_list(
            k, n, combined_filter, actual_sort_key, actual_reverse
        )

    def sort_by_field(self, field, reverse: bool = False) -> None:
        """Делегировать сортировку по имени."""
        return self._repository.sort_by_field(field, reverse)

    def add(self, new_customer: Customer) -> bool:
        """Делегировать добавление клиента."""
        return self._repository.add(new_customer)

    def replace_by_id(self, c_id: int, new_customer: Customer) -> bool:
        """Делегировать замену по ID."""
        return self._repository.replace_by_id(c_id, new_customer)

    def delete_by_id(self, c_id: int) -> bool:
        """Делегировать удаление по ID."""
        return self._repository.delete_by_id(c_id)

    def get_count(
        self, filter_func: Optional[Callable[[Customer], bool]] = None
    ) -> int:
        """Делегировать получение количества."""
        combined_filter = self._combine_filters(filter_func)
        return self._repository.get_count(combined_filter)

    def get_all(self) -> List[Customer]:
        """Делегировать получение всех клиентов."""
        return self._repository.get_all()

    def add_filter_function(
        self, filter_func: Callable[[Customer], bool]
    ) -> "FileRepositoryDecorator":
        """
        Добавить функцию-фильтр.

        Args:
            filter_func: функция, принимающая Customer и возвращающая bool

        Returns:
            self для цепочки вызовов
        """
        self._filter_functions.append(filter_func)
        return self

    def set_sorting_function(
        self,
        sort_key: Optional[Callable[[Customer], Any]] = None,
        reverse: bool = False,
    ) -> "FileRepositoryDecorator":
        """
        Установить функцию сортировки.

        Args:
            sort_key: функция для извлечения ключа сортировки
            reverse: обратный порядок сортировки

        Returns:
            self для цепочки вызовов
        """
        self._sort_key = sort_key
        self._reverse = reverse
        return self

    def clear_filters(self) -> "FileRepositoryDecorator":
        """
        Очистить все фильтры.

        Returns:
            self для цепочки вызовов
        """
        self._filter_functions = []
        return self

    def _combine_filters(
        self, additional_filter: Optional[Callable[[Customer], bool]]
    ) -> Optional[Callable[[Customer], bool]]:
        """Объединить фильтры."""
        if not self._filter_functions and additional_filter is None:
            return None

        def combined_filter(customer: Customer) -> bool:
            # Применяем все фильтры декоратора
            for filter_func in self._filter_functions:
                if not filter_func(customer):
                    return False

            # Применяем дополнительный фильтр
            if additional_filter is not None and not additional_filter(customer):
                return False

            return True

        return combined_filter


class FileCustomerFilters:
    """Коллекция готовых фильтров для работы с файлами."""

    @staticmethod
    def name_starts_with(prefix: str) -> Callable[[Customer], bool]:
        """
        Фильтр по началу имени.

        Args:
            prefix: префикс для поиска

        Returns:
            Функция-фильтр
        """

        def filter_func(customer: Customer) -> bool:
            return customer.name.lower().startswith(prefix.lower())

        return filter_func

    @staticmethod
    def name_contains(substring: str) -> Callable[[Customer], bool]:
        """
        Фильтр по подстроке в имени.

        Args:
            substring: подстрока для поиска

        Returns:
            Функция-фильтр
        """

        def filter_func(customer: Customer) -> bool:
            return substring.lower() in customer.name.lower()

        return filter_func

    @staticmethod
    def address_contains(city: str) -> Callable[[Customer], bool]:
        """
        Фильтр по городу в адресе.

        Args:
            city: город для поиска

        Returns:
            Функция-фильтр
        """

        def filter_func(customer: Customer) -> bool:
            return city.lower() in customer.address.lower()

        return filter_func

    @staticmethod
    def phone_matches(pattern: str) -> Callable[[Customer], bool]:
        """
        Фильтр по шаблону телефона.

        Args:
            pattern: регулярное выражение

        Returns:
            Функция-фильтр
        """

        def filter_func(customer: Customer) -> bool:
            return bool(re.search(pattern, customer.phone))

        return filter_func

    @staticmethod
    def composite_filter(
        *filters: Callable[[Customer], bool]
    ) -> Callable[[Customer], bool]:
        """
        Композитный фильтр (логическое И).

        Args:
            *filters: список фильтров

        Returns:
            Композитная функции-фильтр
        """

        def filter_func(customer: Customer) -> bool:
            return all(func(customer) for func in filters)

        return filter_func


class FileCustomerSort:
    """Коллекция готовых функций сортировки для работы с файлами."""

    @staticmethod
    def by_id() -> Callable[[Customer], Any]:
        """Сортировка по ID."""
        return lambda x: x.customer_id

    @staticmethod
    def by_name() -> Callable[[Customer], Any]:
        """Сортировка по имени."""
        return lambda x: x.name.lower()

    @staticmethod
    def by_address() -> Callable[[Customer], Any]:
        """Сортировка по адресу."""
        return lambda x: x.address.lower()

    @staticmethod
    def by_phone() -> Callable[[Customer], Any]:
        """Сортировка по телефону."""
        return lambda x: x.phone

    @staticmethod
    def by_contact_person() -> Callable[[Customer], Any]:
        """Сортировка по контактному лицу."""
        return lambda x: x.contact_person.lower()