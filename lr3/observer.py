from abc import ABC, abstractmethod
from typing import List, Any


class Observer(ABC):
    """Абстрактный класс наблюдателя."""

    @abstractmethod
    def update(self, subject: Any, data: Any = None):
        """
        Обновление наблюдателя.

        Args:
            subject: объект, который отправил обновление
            data: дополнительные данные
        """
        pass


class Observable:
    """Класс наблюдаемого объекта."""

    def __init__(self):
        self._observers: List[Observer] = []

    def add_observer(self, observer: Observer):
        """Добавить наблюдателя."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: Observer):
        """Удалить наблюдателя."""
        if observer in self._observers:
            self._observers.remove(observer)

    def notify_observers(self, data: Any = None):
        """Уведомить всех наблюдателей."""
        for observer in self._observers:
            observer.update(self, data)