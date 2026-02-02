import urllib.parse
from models.customer import Customer, ValidationError


class CustomerFormController:
    """Контроллер формы клиента (добавление и редактирование)."""

    def __init__(self, repository, mode='add'):
        self.repository = repository
        self.mode = mode  # 'add' или 'edit'

    def handle_request(self, environ):
        """Обработка HTTP запросов."""
        method = environ.get('REQUEST_METHOD', 'GET')

        if method == 'GET':
            return self.handle_get(environ)
        elif method == 'POST':
            return self.handle_post(environ)
        else:
            from views.customer_form_view import CustomerFormView
            view = CustomerFormView(self, self.mode)
            return view.render_error("Неверный метод запроса")

    def handle_get(self, environ):
        """Обработка GET запроса."""
        from views.customer_form_view import CustomerFormView
        view = CustomerFormView(self, self.mode)

        if self.mode == 'edit':
            # Получаем ID клиента для редактирования
            query_string = environ.get('QUERY_STRING', '')
            params = urllib.parse.parse_qs(query_string)
            customer_id = int(params.get('id', [0])[0])
            customer = self.repository.get_by_id(customer_id)

            if customer:
                return view.render_form(customer)
            else:
                return view.render_error("Клиент не найден")
        else:
            # Для добавления показываем пустую форму
            return view.render_form()

    def handle_post(self, environ):
        """Обработка POST запроса."""
        from views.customer_form_view import CustomerFormView
        view = CustomerFormView(self, self.mode)

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

            if self.mode == 'edit':
                # Для редактирования нужен ID
                customer_id = int(post_data.get('customer_id', [0])[0])

                # Создаем объект для валидации
                try:
                    temp_customer = Customer(
                        customer_id=customer_id,
                        name=name,
                        address=address,
                        phone=phone,
                        contact_person=contact_person
                    )

                    # Обновляем клиента
                    if self.repository.update(customer_id, customer_data):
                        return view.render_success("Клиент успешно обновлен")
                    else:
                        return view.render_error("Не удалось обновить клиента")

                except ValidationError as e:
                    return view.render_error(f"Ошибка валидации: {str(e)}")
            else:
                # Для добавления
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