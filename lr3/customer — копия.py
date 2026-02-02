import json
import re
from typing import Optional, Dict, Any


class ValidationError(Exception):
    """Исключение для ошибок валидации."""


def validate_name(name: str, field_name: str = "Имя") -> str:
    """Валидация имени."""
    if not isinstance(name, str):
        raise ValidationError(f"{field_name} должно быть строкой")

    name = name.strip()
    if len(name) < 2:
        raise ValidationError(f"{field_name} должно содержать минимум 2 символа")
    if len(name) > 100:
        raise ValidationError(f"{field_name} должно содержать максимум 100 символов")

    if not re.match(r'^[a-zA-Zа-яА-ЯёЁ\s\-\.,\'\"\(\)\d]+$', name):
        raise ValidationError(f"{field_name} содержит недопустимые символы")

    return name


def validate_phone(phone: str) -> str:
    """Валидация телефона."""
    if not isinstance(phone, str):
        raise ValidationError("Телефон должен быть строкой")

    phone = phone.strip()
    digits = re.sub(r'\D', '', phone)

    # Исправлено: от 5 до 20 цифр
    if len(digits) < 5:
        raise ValidationError("Телефон должен содержать минимум 5 цифр")
    if len(digits) > 20:
        raise ValidationError("Телефон должен содержать максимум 20 цифр")

    if not re.match(r'^[\d\s\-\+\(\)]+$', phone):
        raise ValidationError("Телефон содержит недопустимые символы")

    return phone


def validate_address(address: str) -> str:
    """Валидация адреса."""
    if not isinstance(address, str):
        raise ValidationError("Адрес должен быть строкой")

    address = address.strip()
    if len(address) < 5:
        raise ValidationError("Адрес должен содержать минимум 5 символов")
    if len(address) > 200:
        raise ValidationError("Адрес должен содержать максимум 200 символов")

    return address


def validate_id(customer_id: int) -> int:
    """Валидация ID."""
    if not isinstance(customer_id, int):
        raise ValidationError("ID должен быть целым числом")
    if customer_id < 0:
        raise ValidationError("ID должен быть положительным числом")
    return customer_id


class ShortCustomer:
    """Краткая версия клиента (только основные данные)."""

    def __init__(self, customer_id: int, name: str, phone: str, contact_person: str):
        """
        Инициализация краткой версии клиента.
        """
        self._customer_id = validate_id(customer_id)
        self._name = validate_name(name, "Наименование")
        self._phone = validate_phone(phone)
        self._contact_person = validate_name(contact_person, "Контактное лицо")

    @property
    def customer_id(self) -> int:
        """Получить идентификатор клиента."""
        return self._customer_id

    @customer_id.setter
    def customer_id(self, value: int):
        """Установить идентификатор клиента."""
        self._customer_id = validate_id(value)

    @property
    def name(self) -> str:
        """Получить имя клиента."""
        return self._name

    @name.setter
    def name(self, value: str):
        """Установить имя клиента."""
        self._name = validate_name(value, "Наименование")

    @property
    def phone(self) -> str:
        """Получить телефон клиента."""
        return self._phone

    @phone.setter
    def phone(self, value: str):
        """Установить телефон клиента."""
        self._phone = validate_phone(value)

    @property
    def contact_person(self) -> str:
        """Получить контактное лицо."""
        return self._contact_person

    @contact_person.setter
    def contact_person(self, value: str):
        """Установить контактное лицо."""
        self._contact_person = validate_name(value, "Контактное лицо")

    def to_short_string(self) -> str:
        """Краткое строковое представление клиента."""
        return f"ID: {self.customer_id}, Name: {self.name}, Phone: {self.phone}, Contact: {self.contact_person}"

    def to_json(self) -> str:
        """Преобразовать в JSON строку."""
        return json.dumps(
            {
                "customer_id": self.customer_id,
                "name": self.name,
                "phone": self.phone,
                "contact_person": self.contact_person,
            },
            ensure_ascii=False,
        )

    def __str__(self) -> str:
        """Строковое представление."""
        return f"ShortCustomer(id={self._customer_id}, name='{self._name}', phone='{self._phone}', contact='{self._contact_person}')"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "contact_person": self.contact_person,
        }

    def __eq__(self, other: object) -> bool:
        """Сравнение объектов."""
        if not isinstance(other, ShortCustomer):
            return False
        return (
            self._customer_id == other._customer_id and
            self._name == other._name and
            self._phone == other._phone and
            self._contact_person == other._contact_person
        )

    def __hash__(self) -> int:
        """Хэш объекта."""
        return hash((self._customer_id, self._name, self._phone, self._contact_person))


class Customer(ShortCustomer):
    """Расширенный класс клиента с полной информацией."""

    def __init__(
        self,
        customer_id: int = 0,
        name: str = "",
        address: str = "",
        phone: str = "",
        contact_person: str = "",
        json_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Инициализация клиента.
        """
        if json_data:
            super().__init__(
                json_data.get("customer_id", 0),
                json_data.get("name", ""),
                json_data.get("phone", ""),
                json_data.get("contact_person", "")
            )
            self._address = validate_address(json_data.get("address", ""))
        else:
            super().__init__(customer_id, name, phone, contact_person)
            self._address = validate_address(address)

    @property
    def address(self) -> str:
        """Получить адрес клиента."""
        return self._address

    @address.setter
    def address(self, value: str):
        """Установить адрес клиента."""
        self._address = validate_address(value)

    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]) -> "Customer":
        """Создать объект из словаря."""
        return cls(
            customer_id=data_dict.get("customer_id", 0),
            name=data_dict.get("name", ""),
            address=data_dict.get("address", ""),
            phone=data_dict.get("phone", ""),
            contact_person=data_dict.get("contact_person", ""),
        )

    @classmethod
    def from_json(cls, json_string: str) -> "Customer":
        """Создать объект из JSON строки."""
        data = json.loads(json_string)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """Строковое представление клиента."""
        return (
            f"Customer(id={self._customer_id}, name='{self._name}', "
            f"address='{self._address}', phone='{self._phone}', "
            f"contact_person='{self._contact_person}')"
        )

    def display_short(self) -> str:
        """Краткое отображение."""
        return f"Клиент #{self._customer_id}: {self._name} ({self._phone}) - {self._contact_person}"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь."""
        base_dict = super().to_dict()
        base_dict.update(
            {"address": self._address}
        )
        return base_dict

    def to_json(self) -> str:
        """Преобразовать в JSON строку с полной информацией."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    def __eq__(self, other: object) -> bool:
        """Сравнение объектов."""
        if not isinstance(other, Customer):
            return False
        return (
            super().__eq__(other)
            and self._address == other._address
        )

    def __hash__(self) -> int:
        """Хэш объекта."""
        return hash(
            (
                self._customer_id,
                self._name,
                self._phone,
                self._contact_person,
                self._address,
            )
        )