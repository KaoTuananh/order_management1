from models.customer_repository import CustomerRepository
from views.main_view import MainView
import urllib.parse


class MainController:
    """Главный контроллер."""

    def __init__(self):
        self.repository = CustomerRepository()
        self.view = MainView(self)
        # Регистрируем представление как наблюдателя
        self.repository.add_observer(self.view)

    def filter_customers(self, environ):
        """Фильтрация клиентов."""
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)

        filter_type = params.get('filter_type', ['name'])[0]
        filter_value = params.get(filter_type, [''])[0]

        # Сохраняем текущие параметры
        current_params = {}
        sort_by = params.get('sort', ['customer_id'])[0]
        reverse = params.get('reverse', ['false'])[0].lower()
        page = params.get('page', [1])[0]

        current_params['sort'] = sort_by
        current_params['reverse'] = reverse
        current_params['page'] = page
        current_params['filter_type'] = filter_type

        if filter_value:
            if filter_type == 'name':
                current_params['filter_name'] = filter_value
            elif filter_type == 'phone':
                current_params['filter_phone'] = filter_value
            elif filter_type == 'address':
                current_params['filter_address'] = filter_value

        # Собираем строку запроса
        query_parts = []
        for key, value in current_params.items():
            query_parts.append(f"{key}={urllib.parse.quote(str(value))}")

        query_string = '&'.join(query_parts)
        url = f'/?{query_string}' if query_string else '/'

        return self.view.render_redirect(url)

    def show_index(self, environ):
        """Показать главную страницу."""
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)

        page = int(params.get('page', [1])[0])
        sort_by = params.get('sort', ['customer_id'])[0]
        reverse = params.get('reverse', ['false'])[0].lower() == 'true'

        # Параметры фильтрации
        filter_name = params.get('filter_name', [None])[0]
        filter_phone = params.get('filter_phone', [None])[0]
        filter_address = params.get('filter_address', [None])[0]
        filter_type = params.get('filter_type', ['name'])[0]

        customers_per_page = 10

        # Создаем фильтрующую функцию - ИСПОЛЬЗОВАНИЕ ИЗ ПРЕДЫДУЩЕЙ ЛР
        filter_func = None
        if filter_type == 'name' and filter_name:
            filter_func = lambda c: filter_name.lower() in c.name.lower()
        elif filter_type == 'phone' and filter_phone:
            filter_func = lambda c: filter_phone.lower() in c.phone.lower()
        elif filter_type == 'address' and filter_address:
            filter_func = lambda c: filter_address.lower() in c.address.lower()

        # Получаем отсортированный список с фильтрацией
        short_list = self.repository.get_k_n_short_list(
            page, customers_per_page, filter_func, sort_by, reverse
        )

        total_count = self.repository.get_count(filter_func)
        total_pages = max(1, (total_count + customers_per_page - 1) // customers_per_page)

        # Генерируем ссылки для сортировки
        sort_links = {}
        for field in ['customer_id', 'name', 'phone', 'address', 'contact_person']:
            if field == sort_by:
                sort_links[field] = f'/?sort={field}&reverse={str(not reverse).lower()}'
            else:
                sort_links[field] = f'/?sort={field}&reverse=false'

            # Добавляем параметры фильтрации
            sort_links[field] += f'&filter_type={filter_type}'
            if filter_type == 'name' and filter_name:
                sort_links[field] += f'&filter_name={urllib.parse.quote(filter_name)}'
            elif filter_type == 'phone' and filter_phone:
                sort_links[field] += f'&filter_phone={urllib.parse.quote(filter_phone)}'
            elif filter_type == 'address' and filter_address:
                sort_links[field] += f'&filter_address={urllib.parse.quote(filter_address)}'

            if page > 1:
                sort_links[field] += f'&page={page}'

        return self.view.render_index(
            short_list,
            page,
            total_pages,
            sort_by,
            reverse,
            filter_type,
            filter_name,
            filter_phone,
            filter_address,
            sort_links
        )