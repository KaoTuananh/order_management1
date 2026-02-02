from models.customer_repository import CustomerRepository, SortField
from views.main_view import MainView
import urllib.parse


class MainController:
    """Главный контроллер."""

    def sort_customers(self, environ):
        """Сортировка клиентов - ИСПОЛЬЗОВАНИЕ ИЗ ПРЕДЫДУЩЕЙ ЛР."""
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)

        sort_by = params.get('field', ['name'])[0]
        reverse = params.get('reverse', ['false'])[0].lower() == 'true'

        # ИСПОЛЬЗОВАНИЕ SortField ИЗ ПРЕДЫДУЩЕЙ ЛР
        field_map = {
            'customer_id': SortField.CUSTOMER_ID,
            'name': SortField.NAME,
            'address': SortField.ADDRESS,
            'phone': SortField.PHONE,
            'contact_person': SortField.CONTACT_PERSON
        }

        if sort_by in field_map:
            self.repository.sort_by_field(field_map[sort_by], reverse)

        # Собираем строку запроса для редиректа
        current_params = {}
        filter_type = params.get('filter_type', ['name'])[0]
        current_params['filter_type'] = filter_type

        if filter_type == 'name':
            filter_name = params.get('filter_name', [None])[0]
            if filter_name:
                current_params['filter_name'] = filter_name
        elif filter_type == 'phone':
            filter_phone = params.get('filter_phone', [None])[0]
            if filter_phone:
                current_params['filter_phone'] = filter_phone
        elif filter_type == 'address':
            filter_address = params.get('filter_address', [None])[0]
            if filter_address:
                current_params['filter_address'] = filter_address

        page = params.get('page', [1])[0]
        current_params['page'] = page
        current_params['sort'] = sort_by
        current_params['reverse'] = str(reverse).lower()

        query_parts = []
        for key, value in current_params.items():
            query_parts.append(f"{key}={urllib.parse.quote(str(value))}")

        query_string = '&'.join(query_parts)
        url = f'/?{query_string}' if query_string else '/'

        return self.view.render_redirect(url)

    def show_index(self, environ):
        """Показать главную страницу с сортировкой."""
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)

        page = int(params.get('page', [1])[0])
        sort_by = params.get('sort', ['customer_id'])[0]  # ПАРАМЕТР СОРТИРОВКИ
        reverse = params.get('reverse', ['false'])[0].lower() == 'true'

        # Получаем отсортированный список - ИСПОЛЬЗОВАНИЕ ЛОГИКИ СОРТИРОВКИ
        short_list = self.repository.get_k_n_short_list(
            page, customers_per_page, filter_func, sort_by, reverse
        )

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
            # ... остальные параметры

        return self.view.render_index(
            short_list,
            page,
            total_pages,
            sort_by,  # ПЕРЕДАЕМ ПАРАМЕТРЫ СОРТИРОВКИ
            reverse,
            filter_type,
            filter_name,
            filter_phone,
            filter_address,
            sort_links
        )