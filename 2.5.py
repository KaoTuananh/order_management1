"""
Репозиторий для работы с базой данных PostgreSQL.
Реализует пункты 4 и 5 (Singleton).
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Optional, Dict, Any, Callable
from entities import Customer, ShortCustomer, ValidationError
from repository_base import CustomerRepBase, SortField


class DBConnection:
    """Singleton для управления подключением к базе данных."""

    _instance: Optional["DBConnection"] = None

    def __new__(cls, db_config: Optional[Dict[str, Any]] = None) -> "DBConnection":
        """
        Создание или получение существующего экземпляра подключения.

        Args:
            db_config: конфигурация подключения к БД

        Returns:
            Единственный экземпляр подключения
        """
        if cls._instance is None:
            if db_config is None:
                raise ValueError(
                    "Конфигурация БД должна быть передана при первом создании!"
                )
            cls._instance = super().__new__(cls)
            cls._instance._db_config = db_config
        return cls._instance

    def execute_query(
        self, query: str, params: Optional[tuple] = None, fetch: bool = False
    ) -> Any:
        """
        Выполнить SQL запрос.

        Args:
            query: SQL запрос
            params: параметры запроса
            fetch: флаг получения результатов

        Returns:
            Результаты запроса или None
        """
        try:
            with psycopg2.connect(**self._db_config) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, params)
                    if fetch:
                        return cursor.fetchall()
                    conn.commit()
        except psycopg2.Error as e:
            print(f"Ошибка выполнения запроса: {e}")
            return None

    def execute_insert(self, query: str, params: Optional[tuple] = None) -> Optional[int]:
        """
        Выполнить INSERT запрос с возвратом ID.

        Args:
            query: SQL INSERT запрос
            params: параметры запроса

        Returns:
            ID новой записи
        """
        try:
            with psycopg2.connect(**self._db_config) as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, params)
                    new_id = cursor.fetchone()[0]
                    conn.commit()
                    return new_id
        except psycopg2.Error as e:
            print(f"Ошибка вставки: {e}")
            return None


class CustomerRepDB(CustomerRepBase):
    """Репозиторий для работы с базой данных PostgreSQL."""

    def __init__(self, db_config: Optional[Dict[str, Any]] = None):
        """
        Инициализация репозитория БД.

        Args:
            db_config: конфигурация подключения к БД
        """
        self._db_config = db_config
        self._db: Optional[DBConnection] = None
        self._data_list: List[Customer] = []

        if db_config:
            try:
                self._db = DBConnection(db_config)
                self._initialize_table()
                self.read_from_file()
            except Exception as e:
                print(f"Ошибка подключения к БД: {e}")
                self._db = None

    def _initialize_table(self) -> None:
        """Инициализировать таблицу в БД, если её нет."""
        if self._db:
            query = """
            CREATE TABLE IF NOT EXISTS customers (
                customer_id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                address VARCHAR(200),
                phone VARCHAR(20),
                contact_person VARCHAR(100)
            )
            """
            self._db.execute_query(query)

    def read_from_file(self) -> None:
        """Чтение данных из таблицы customers."""
        if self._db:
            query = "SELECT * FROM customers ORDER BY customer_id"
            rows = self._db.execute_query(query, fetch=True)
            if rows:
                self._data_list = []
                for row in rows:
                    try:
                        customer = Customer(
                            customer_id=row["customer_id"],
                            name=row["name"],
                            address=row["address"],
                            phone=row["phone"],
                            contact_person=row["contact_person"],
                        )
                        self._data_list.append(customer)
                    except ValidationError as e:
                        print(f"Ошибка валидации данных из БД: {e}")
                        continue

    def write_to_file(self) -> None:
        """Для БД изменения сохраняются сразу при операциях."""
        pass

    def get_by_id(self, c_id: int) -> Optional[Customer]:
        """Получить клиента по ID из БД."""
        if self._db:
            query = "SELECT * FROM customers WHERE customer_id = %s"
            rows = self._db.execute_query(query, (c_id,), fetch=True)
            if rows:
                row = rows[0]
                try:
                    return Customer(
                        customer_id=row["customer_id"],
                        name=row["name"],
                        address=row["address"],
                        phone=row["phone"],
                        contact_person=row["contact_person"],
                    )
                except ValidationError as e:
                    print(f"Ошибка валидации данных: {e}")
        return None

    def get_k_n_short_list(
        self,
        k: int,
        n: int,
        filter_func: Optional[Callable[[Customer], bool]] = None,
        sort_key: Optional[Callable[[Customer], Any]] = None,
        reverse: bool = False,
    ) -> List[ShortCustomer]:
        """Получить короткий список клиентов с пагинацией из БД."""
        # Сначала получаем все данные
        self.read_from_file()

        # Фильтрация в памяти (для простоты)
        filtered_data = (
            self._data_list
            if filter_func is None
            else [c for c in self._data_list if filter_func(c)]
        )

        # Сортировка
        if sort_key:
            filtered_data.sort(key=sort_key, reverse=reverse)
        else:
            filtered_data.sort(key=lambda x: x.customer_id)

        # Пагинация
        start = (k - 1) * n
        end = start + n
        paginated_data = filtered_data[start:end]

        # Преобразуем в ShortCustomer
        result = []
        for customer in paginated_data:
            result.append(ShortCustomer(customer.customer_id, customer.name, customer.phone))
        return result

    def sort_by_field(self, field: SortField, reverse: bool = False) -> None:
        """Отсортировать клиентов по указанному полю в БД."""
        if not self._db:
            return

        field_mapping = {
            SortField.CUSTOMER_ID: "customer_id",
            SortField.NAME: "name",
            SortField.ADDRESS: "address",
            SortField.PHONE: "phone",
            SortField.CONTACT_PERSON: "contact_person",
        }

        if field not in field_mapping:
            raise ValueError(f"Поле {field} недоступно для сортировки")

        sql_field = field_mapping[field]
        order = "DESC" if reverse else "ASC"

        query = f"SELECT * FROM customers ORDER BY {sql_field} {order}"
        rows = self._db.execute_query(query, fetch=True)

        if rows:
            self._data_list = []
            for row in rows:
                try:
                    customer = Customer(
                        customer_id=row["customer_id"],
                        name=row["name"],
                        address=row["address"],
                        phone=row["phone"],
                        contact_person=row["contact_person"],
                    )
                    self._data_list.append(customer)
                except ValidationError as e:
                    print(f"Ошибка валидации данных: {e}")
                    continue

    def add(self, new_customer: Customer) -> bool:
        """Добавить клиента в БД."""
        if self._db:
            query = """
                INSERT INTO customers (name, address, phone, contact_person)
                VALUES (%s, %s, %s, %s) RETURNING customer_id
            """
            params = (
                new_customer.name,
                new_customer.address,
                new_customer.phone,
                new_customer.contact_person,
            )
            new_id = self._db.execute_insert(query, params)
            if new_id:
                new_customer.customer_id = new_id
                self._data_list.append(new_customer)
                return True
        return False

    def replace_by_id(self, c_id: int, new_customer: Customer) -> bool:
        """Заменить клиента по ID в БД."""
        if self._db:
            # Сначала проверим существование
            existing = self.get_by_id(c_id)
            if not existing:
                return False

            query = """
                UPDATE customers 
                SET name = %s, address = %s, phone = %s, contact_person = %s
                WHERE customer_id = %s
            """
            params = (
                new_customer.name,
                new_customer.address,
                new_customer.phone,
                new_customer.contact_person,
                c_id,
            )
            result = self._db.execute_query(query, params)
            if result is not None:
                # Обновить локальный список
                new_customer.customer_id = c_id
                for i, customer in enumerate(self._data_list):
                    if customer.customer_id == c_id:
                        self._data_list[i] = new_customer
                        return True
        return False

    def delete_by_id(self, c_id: int) -> bool:
        """Удалить клиента по ID из БД."""
        if self._db:
            # Сначала проверим существование
            existing = self.get_by_id(c_id)
            if not existing:
                return False

            query = "DELETE FROM customers WHERE customer_id = %s"
            result = self._db.execute_query(query, (c_id,))
            if result is not None:
                # Удалить из локального списка
                for i, customer in enumerate(self._data_list):
                    if customer.customer_id == c_id:
                        del self._data_list[i]
                        return True
        return False

    def get_count(
        self, filter_func: Optional[Callable[[Customer], bool]] = None
    ) -> int:
        """Получить количество клиентов из БД."""
        if filter_func is None:
            if self._db:
                query = "SELECT COUNT(*) as count FROM customers"
                rows = self._db.execute_query(query, fetch=True)
                if rows:
                    return rows[0]["count"]
            return len(self._data_list)
        else:
            # Фильтрация в памяти
            return len([c for c in self._data_list if filter_func(c)])

    def get_all(self) -> List[Customer]:
        """Получить всех клиентов."""
        return self._data_list.copy()