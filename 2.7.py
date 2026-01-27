"""
Декоратор для репозитория БД с фильтрацией и сортировкой.
Реализует пункт 7.
"""

from typing import List, Optional, Dict, Any, Callable
from repository_base import CustomerRepBase
from entities import Customer, ShortCustomer


class RepositoryDecorator(CustomerRepBase):
    """Базовый декоратор для репозиториев."""

    def __init__(self, repository: CustomerRepBase):
        """
        Инициализация декоратора.

        Args:
            repository: декорируемый репозиторий
        """
        self._repository = repository

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
        return self._repository.get_k_n_short_list(k, n, filter_func, sort_key, reverse)

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
        return self._repository.get_count(filter_func)

    def get_all(self) -> List[Customer]:
        """Делегировать получение всех клиентов."""
        return self._repository.get_all()


class DBDecoratorWithFilter(RepositoryDecorator):
    """
    Декоратор для репозитория БД с фильтрацией и сортировкой.
    Позволяет передавать фильтры и способы сортировки в методы.
    """

    def __init__(self, repository: CustomerRepBase):
        """
        Инициализация декоратора.

        Args:
            repository: декорируемый репозиторий
        """
        super().__init__(repository)
        self._filter_functions: List[Callable[[Customer], bool]] = []
        self._sort_key: Optional[Callable[[Customer], Any]] = None
        self._reverse = False

    def add_filter_function(
        self, filter_func: Callable[[Customer], bool]
    ) -> "DBDecoratorWithFilter":
        """
        Добавить функцию-фильтр.

        Args:
            filter_func: функция, принимающая Customer и возвращающая bool

        Returns:
            self для цепочки вызовов
        """
        self._filter_functions.append(filter_func)
        return self

    def set_sorting(
        self,
        sort_key: Optional[Callable[[Customer], Any]] = None,
        reverse: bool = False,
    ) -> "DBDecoratorWithFilter":
        """
        Установить сортировку.

        Args:
            sort_key: функция для извлечения ключа сортировки
            reverse: обратный порядок сортировки

        Returns:
            self для цепочки вызовов
        """
        self._sort_key = sort_key
        self._reverse = reverse
        return self

    def clear_filters(self) -> "DBDecoratorWithFilter":
        """
        Очистить все фильтры.

        Returns:
            self для цепочки вызовов
        """
        self._filter_functions = []
        return self

    def get_k_n_short_list(
        self,
        k: int,
        n: int,
        filter_func: Optional[Callable[[Customer], bool]] = None,
        sort_key: Optional[Callable[[Customer], Any]] = None,
        reverse: bool = False,
    ) -> List[ShortCustomer]:
        """
        Получить отфильтрованный и отсортированный список.

        Args:
            k: номер страницы
            n: количество элементов на странице
            filter_func: дополнительная функция фильтрации
            sort_key: дополнительная функции сортировки
            reverse: обратный порядок сортировки

        Returns:
            Список ShortCustomer
        """
        # Объединяем фильтры
        combined_filter = self._combine_filters(filter_func)

        # Используем переданную сортировку или дефолтную
        actual_sort_key = sort_key if sort_key is not None else self._sort_key
        actual_reverse = reverse if sort_key is not None else self._reverse

        return self._repository.get_k_n_short_list(
            k, n, combined_filter, actual_sort_key, actual_reverse
        )

    def get_count(
        self, filter_func: Optional[Callable[[Customer], bool]] = None
    ) -> int:
        """
        Получить количество элементов с учетом фильтров.

        Args:
            filter_func: дополнительная функция фильтрации

        Returns:
            Количество отфильтрованных элементов
        """
        combined_filter = self._combine_filters(filter_func)
        return self._repository.get_count(combined_filter)

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