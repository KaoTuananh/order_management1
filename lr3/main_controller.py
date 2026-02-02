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

    def handle_request(self, environ):
        """Обработка HTTP запросов."""
        method = environ.get('REQUEST_METHOD', 'GET')
        path = environ.get('PATH_INFO', '/')

        if path == '/' or path == '/index':
            return self.show_index(environ)
        elif path == '/get_customer_details':
            return self.get_customer_details(environ)
        elif path == '/get_update_count':
            return self.get_update_count()
        else:
            return self.view.render_not_found()

    def show_index(self, environ):
        """Показать главную страницу."""
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)

        page = int(params.get('page', [1])[0])
        customers_per_page = 10

        # Получаем список клиентов
        short_list = self.repository.get_k_n_short_list(page, customers_per_page)

        total_count = self.repository.get_count()
        total_pages = max(1, (total_count + customers_per_page - 1) // customers_per_page)

        return self.view.render_index(short_list, page, total_pages)

    def get_customer_details(self, environ):
        """Получить детали клиента."""
        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)

        customer_id = int(params.get('id', [0])[0])
        customer = self.repository.get_by_id(customer_id)

        from views.customer_details_view import CustomerDetailsView
        view = CustomerDetailsView(self)

        if customer:
            return view.render_details(customer)
        else:
            return view.render_error("Клиент не найден")

    def get_update_count(self):
        """Получить счетчик обновлений Observer."""
        import json
        data = json.dumps({
            'update_count': self.view._update_counter
        }).encode('utf-8')
        return [
            '200 OK',
            [('Content-Type', 'application/json; charset=utf-8'),
             ('Content-Length', str(len(data)))],
            [data]
        ]