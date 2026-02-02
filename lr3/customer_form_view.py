class CustomerFormView:
    """Представление формы клиента."""

    def __init__(self, controller, mode='add'):
        self.controller = controller
        self.mode = mode  # 'add' или 'edit'

    def render_form(self, customer=None):
        """Рендер формы."""
        if self.mode == 'add':
            title = "Добавление нового клиента"
            action = "/add"
            submit_text = "Добавить"
            customer_id = ""
            name = ""
            address = ""
            phone = ""
            contact_person = ""
        else:
            title = "Редактирование клиента"
            action = "/edit"
            submit_text = "Сохранить изменения"
            if customer:
                customer_id = str(customer.customer_id)
                name = customer.name
                address = customer.address
                phone = customer.phone
                contact_person = customer.contact_person
            else:
                customer_id = ""
                name = ""
                address = ""
                phone = ""
                contact_person = ""

        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .container {{ max-width: 600px; }}
                .error-message {{ color: red; font-size: 0.875em; margin-top: 0.25rem; }}
                .is-invalid {{ border-color: #dc3545 !important; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4">{title}</h1>

                <form id="customerForm" action="{action}" method="post" onsubmit="return validateForm()">
                    <input type="hidden" name="customer_id" value="{customer_id}">

                    <div class="mb-3">
                        <label for="name" class="form-label">Наименование *</label>
                        <input type="text" class="form-control" id="name" name="name" value="{name}" required
                               minlength="2" maxlength="100">
                        <div class="form-text">Обязательное поле, 2-100 символов</div>
                        <div class="error-message" id="nameError"></div>
                    </div>

                    <div class="mb-3">
                        <label for="address" class="form-label">Адрес *</label>
                        <textarea class="form-control" id="address" name="address" rows="2" required
                                  minlength="5" maxlength="200">{address}</textarea>
                        <div class="form-text">Обязательное поле, 5-200 символов</div>
                        <div class="error-message" id="addressError"></div>
                    </div>

                    <div class="mb-3">
                        <label for="phone" class="form-label">Телефон *</label>
                        <input type="text" class="form-control" id="phone" name="phone" value="{phone}" required
                               minlength="5" maxlength="20">
                        <div class="form-text">Обязательное поле, 5-20 цифр</div>
                        <div class="error-message" id="phoneError"></div>
                    </div>

                    <div class="mb-3">
                        <label for="contact_person" class="form-label">Контактное лицо *</label>
                        <input type="text" class="form-control" id="contact_person" name="contact_person" value="{contact_person}" required
                               minlength="2" maxlength="100">
                        <div class="form-text">Обязательное поле, 2-100 символов</div>
                        <div class="error-message" id="contactError"></div>
                    </div>

                    <div class="d-flex justify-content-between">
                        <a href="/" class="btn btn-secondary">Отмена</a>
                        <button type="submit" class="btn btn-primary">{submit_text}</button>
                    </div>
                </form>
            </div>

            <script>
            function validateForm() {{
                let isValid = true;

                // Сброс ошибок
                document.querySelectorAll('.error-message').forEach(el => el.textContent = '');
                document.querySelectorAll('.form-control').forEach(el => el.classList.remove('is-invalid'));

                // Валидация имени
                const nameInput = document.getElementById('name');
                const nameValue = nameInput.value.trim();
                if (!nameValue || nameValue.length < 2 || nameValue.length > 100) {{
                    document.getElementById('nameError').textContent = 'Имя должно содержать 2-100 символов';
                    nameInput.classList.add('is-invalid');
                    isValid = false;
                }}

                // Валидация адреса
                const addressInput = document.getElementById('address');
                const addressValue = addressInput.value.trim();
                if (!addressValue || addressValue.length < 5 || addressValue.length > 200) {{
                    document.getElementById('addressError').textContent = 'Адрес должен содержать 5-200 символов';
                    addressInput.classList.add('is-invalid');
                    isValid = false;
                }}

                // Валидация телефона (ИСПРАВЛЕНО: 5-20 цифр)
                const phoneInput = document.getElementById('phone');
                const phoneValue = phoneInput.value.trim();
                const digitsOnly = phoneValue.replace(/\\D/g, '');

                if (!phoneValue) {{
                    document.getElementById('phoneError').textContent = 'Телефон обязателен для заполнения';
                    phoneInput.classList.add('is-invalid');
                    isValid = false;
                }} else if (digitsOnly.length < 5) {{
                    document.getElementById('phoneError').textContent = 'Телефон должен содержать минимум 5 цифр';
                    phoneInput.classList.add('is-invalid');
                    isValid = false;
                }} else if (digitsOnly.length > 20) {{
                    document.getElementById('phoneError').textContent = 'Телефон должен содержать максимум 20 цифр';
                    phoneInput.classList.add('is-invalid');
                    isValid = false;
                }}

                // Валидация контактного лица
                const contactInput = document.getElementById('contact_person');
                const contactValue = contactInput.value.trim();
                if (!contactValue || contactValue.length < 2 || contactValue.length > 100) {{
                    document.getElementById('contactError').textContent = 'Контактное лицо должно содержать 2-100 символов';
                    contactInput.classList.add('is-invalid');
                    isValid = false;
                }}

                if (!isValid) {{
                    // Прокрутка к первой ошибке
                    const firstError = document.querySelector('.is-invalid');
                    if (firstError) {{
                        firstError.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                }}

                return isValid;
            }}

            // Реальная проверка при вводе
            document.addEventListener('DOMContentLoaded', function() {{
                const phoneInput = document.getElementById('phone');
                if (phoneInput) {{
                    phoneInput.addEventListener('input', function(e) {{
                        // Удаляем все символы, кроме разрешенных
                        this.value = this.value.replace(/[^\\d\\s\\-\\+\\(\\)]/g, '');
                    }});
                }}

                const nameInput = document.getElementById('name');
                if (nameInput) {{
                    nameInput.addEventListener('input', function(e) {{
                        // Разрешаем только буквы, цифры, пробелы, дефисы, точки, скобки, апострофы
                        this.value = this.value.replace(/[^a-zA-Zа-яА-ЯёЁ\\s\\-\\.\\,'"()\\d]/g, '');
                    }});
                }}

                const contactInput = document.getElementById('contact_person');
                if (contactInput) {{
                    contactInput.addEventListener('input', function(e) {{
                        // Разрешаем только буквы, цифры, пробелы, дефисы, точки, скобки, апострофы
                        this.value = this.value.replace(/[^a-zA-Zа-яА-ЯёЁ\\s\\-\\.\\,'"()\\d]/g, '');
                    }});
                }}
            }});
            </script>
        </body>
        </html>
        """

        return self._wrap_response(html)

    def render_success(self, message="Операция выполнена успешно"):
        """Рендер страницы успеха."""
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Успешно</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .container {{ max-width: 600px; }}
            </style>
            <meta http-equiv="refresh" content="2;url=/" />
        </head>
        <body>
            <div class="container">
                <div class="alert alert-success mt-4">
                    <h4>Успешно!</h4>
                    <p>{message}</p>
                    <p>Вы будете перенаправлены на главную страницу через 2 секунды...</p>
                    <div class="mt-3">
                        <a href="/" class="btn btn-primary">Вернуться сейчас</a>
                        <button class="btn btn-secondary" onclick="window.opener.location.reload(); window.close();">
                            Закрыть окно и обновить главную
                        </button>
                    </div>
                </div>
            </div>

            <script>
            // Автоматическое обновление главной страницы через паттерн Observer
            window.onload = function() {{
                try {{
                    // Пытаемся обновить родительское окно
                    if (window.opener && !window.opener.closed) {{
                        window.opener.postMessage({{action: 'customer_updated'}}, '*');
                    }}
                }} catch (e) {{
                    console.log('Не удалось обновить родительское окно:', e);
                }}
            }};
            </script>
        </body>
        </html>
        """
        return self._wrap_response(html)

    def render_error(self, message):
        """Рендер страницы ошибки."""
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Ошибка</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                body {{ padding: 20px; }}
                .container {{ max-width: 600px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="alert alert-danger mt-4">
                    <h4>Ошибка!</h4>
                    <p>{message}</p>
                    <div class="mt-3">
                        <button onclick="window.history.back()" class="btn btn-secondary">Назад</button>
                        <a href="/" class="btn btn-primary">На главную</a>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return self._wrap_response(html)

    def _wrap_response(self, html, status='200 OK', content_type='text/html; charset=utf-8'):
        """Обертка для HTTP ответа."""
        response_body = html.encode('utf-8')
        return [
            status,
            [('Content-Type', content_type),
             ('Content-Length', str(len(response_body)))],
            [response_body]
        ]