import urllib.parse


class CustomerDetailsController:
    """Контроллер для просмотра деталей клиента."""

    def __init__(self, repository):
        self.repository = repository

    def handle_request(self, environ):
        """Обработка HTTP запросов."""
        method = environ.get('REQUEST_METHOD', 'GET')

        if method == 'GET':
            return self.handle_get(environ)
        else:
            from views.customer_details_view import CustomerDetailsView
            view = CustomerDetailsView(self)
            return view.render_error("Неверный метод запроса")

    def handle_get(self, environ):
        """Обработка GET запроса."""
        from views.customer_details_view import CustomerDetailsView
        view = CustomerDetailsView(self)

        query_string = environ.get('QUERY_STRING', '')
        params = urllib.parse.parse_qs(query_string)
        customer_id = int(params.get('id', [0])[0])
        customer = self.repository.get_by_id(customer_id)

        if customer:
            return view.render_details(customer)
        else:
            return view.render_error("Клиент не найден")