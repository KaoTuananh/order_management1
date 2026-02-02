import urllib.parse
from models.customer import Customer, ValidationError


class CustomerFormController:
    """Контроллер формы добавления клиента."""

    def __init__(self, repository, mode='add'):
        self.repository = repository
        self.mode = mode

    def handle_request(self, environ):
        """Обработка HTTP запросов."""
        method = environ.get('REQUEST_METHOD', 'GET')

        if method == 'GET':
            return self.handle_get(environ)
        elif method == 'POST':
            return self.handle_post(environ)
        else:
            from views.customer_form_view import CustomerFormView
            view = CustomerFormView(self)
            return view.render_error("Неверный метод запроса")

    def handle_get(self, environ):
        """Обработка GET запроса - показать форму."""
        from views.customer_form_view import CustomerFormView
        view = CustomerFormView(self)
        return view.render_form()

    def handle_post(self, environ):
        """Обработка POST запроса - добавить клиента."""
        from views.customer_form_view import CustomerFormView
        view = CustomerFormView(self)

        try:
            # Читаем тело запроса
            try:
                request_body_size = int(environ.get('CONTENT_LENGTH', 0))
            except ValueError:
                request_body_size = 0

            request_body = environ['wsgi.input'].read(request_body_size)
            post_data = urllib.parse.parse_qs(request_body.decode('utf-8'))

            # Извлекаем данные формы
            name = post_data.get('name', [''])[0]
            address = post_data.get('address', [''])[0]
            phone = post_data.get('phone', [''])[0]
            contact_person = post_data.get('contact_person', [''])[0]

            # Валидация данных
            customer_data = {
                'name': name,
                'address': address,
                'phone': phone,
                'contact_person': contact_person
            }

            try:
                # Создаем временный клиент для проверки валидации
                temp_customer = Customer(
                    customer_id=0,  # Временный ID
                    name=name,
                    address=address,
                    phone=phone,
                    contact_person=contact_person
                )

                # Добавляем клиента
                if self.repository.add(customer_data):
                    return view.render_success("Клиент успешно добавлен")
                else:
                    return view.render_error("Не удалось добавить клиента")

            except ValidationError as e:
                return view.render_error(f"Ошибка валидации: {str(e)}")

        except ValidationError as e:
            return view.render_error(f"Ошибка валидации: {str(e)}")
        except ValueError as e:
            return view.render_error(f"Ошибка значения: {str(e)}")
        except Exception as e:
            return view.render_error(f"Ошибка: {str(e)}")