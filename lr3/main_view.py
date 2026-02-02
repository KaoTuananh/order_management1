from models.observer import Observer
import urllib.parse


class MainView(Observer):
    """Главное представление с поддержкой Observer."""

    def __init__(self, controller):
        self.controller = controller
        self._update_counter = 0

    def update(self, subject, data=None):
        """
        Обновление представления через паттерн Наблюдатель.
        Вызывается при изменении данных в репозитории.
        """
        self._update_counter += 1
        print(f"[Observer] Получено обновление #{self._update_counter} от {subject.__class__.__name__}")

        if data:
            print(f"[Observer] Данные обновления: {data}")

        # В реальном приложении здесь можно было бы
        # отправлять WebSocket сообщения или SSE для обновления UI
        # В текущей реализации обновление происходит через redirect

    def render_index(self, customers, page, total_pages):
        """Рендер главной страницы."""
        customers_html = ""
        for customer in customers:
            customers_html += f"""
            <tr>
                <td>{customer.customer_id}</td>
                <td>{customer.name}</td>
                <td>{customer.phone}</td>
                <td>{customer.contact_person}</td>
                <td>
                    <a href="/get_customer_details?id={customer.customer_id}" class="btn btn-info btn-sm" target="_blank">Просмотр</a>
                </td>
            </tr>
            """

        pagination_html = ""
        if total_pages > 1:
            pagination_html = '<nav><ul class="pagination justify-content-center">'

            # Кнопка "Назад"
            if page > 1:
                pagination_html += f'<li class="page-item"><a class="page-link" href="/?page={page - 1}">← Назад</a></li>'

            # Номера страниц
            for p in range(1, total_pages + 1):
                active = "active" if p == page else ""
                if p == 1 or p == total_pages or (p >= page - 2 and p <= page + 2):
                    pagination_html += f'<li class="page-item {active}"><a class="page-link" href="/?page={p}">{p}</a></li>'
                elif p == page - 3 or p == page + 3:
                    pagination_html += '<li class="page-item disabled"><span class="page-link">...</span></li>'

            # Кнопка "Вперед"
            if page < total_pages:
                pagination_html += f'<li class="page-item"><a class="page-link" href="/?page={page + 1}">Вперед →</a></li>'

            pagination_html += '</ul></nav>'

        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Управление клиентами</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/static/css/style.css">
            <script>
            // Инициализация счетчика обновлений Observer
            let updateCounter = 0;

            function handleObserverUpdate(data) {{
                updateCounter++;
                console.log(`Обновление #${{updateCounter}}:`, data);

                // Можно добавить визуальное уведомление
                if (data && data.action) {{
                    showNotification(`${{data.action}} выполнено`);
                }}
            }}

            function showNotification(message) {{
                // Создаем уведомление
                const notification = document.createElement('div');
                notification.className = 'alert alert-success alert-dismissible fade show position-fixed';
                notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
                notification.innerHTML = `
                    <strong>Обновление:</strong> ${{message}}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                document.body.appendChild(notification);

                // Автоматическое скрытие через 3 секунды
                setTimeout(() => {{
                    if (notification.parentNode) {{
                        notification.remove();
                    }}
                }}, 3000);
            }}
            </script>
        </head>
        <body>
            <div class="container mt-4">
                <h1 class="mb-4">Управление клиентами</h1>

                <div class="mb-4">
                    <button class="btn btn-secondary" onclick="location.reload()">Обновить</button>
                    <span class="badge bg-info ms-2">Обновлений: <span id="updateCounter">0</span></span>
                </div>

                <div class="card">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <h5 class="mb-0">Список клиентов</h5>
                        <span class="badge bg-primary">Всего: {len(customers)} из {self.controller.repository.get_count()}</span>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Имя</th>
                                        <th>Телефон</th>
                                        <th>Контактное лицо</th>
                                        <th>Действия</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {customers_html if customers_html else '<tr><td colspan="5" class="text-center">Клиенты не найдены</td></tr>'}
                                </tbody>
                            </table>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <div class="text-muted">
                                Страница {page} из {total_pages}
                            </div>
                            {pagination_html}
                        </div>
                    </div>
                </div>
            </div>

            <script>
            // Инициализируем счетчик обновлений
            document.addEventListener('DOMContentLoaded', function() {{
                const counterElement = document.getElementById('updateCounter');
                if (counterElement) {{
                    setInterval(() => {{
                        // В реальном приложении здесь бы был WebSocket или SSE
                        // Для демонстрации просто обновляем счетчик
                        fetch('/get_update_count')
                            .then(response => response.json())
                            .then(data => {{
                                if (data.update_count) {{
                                    counterElement.textContent = data.update_count;
                                }}
                            }});
                    }}, 5000);
                }}
            }});

            // Обработка сообщений от дочерних окон (паттерн Observer)
            window.addEventListener('message', function(event) {{
                if (event.data && event.data.action === 'customer_details_opened') {{
                    console.log(`Детали клиента #${{event.data.customer_id}} открыты в отдельной вкладке`);
                    showNotification(`Детали клиента #${{event.data.customer_id}} открыты`);
                }}
            }});
            </script>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
            <script src="/static/js/main.js"></script>
        </body>
        </html>
        """

        return self._wrap_response(html)

    def render_customer_details(self, customer):
        """Рендер деталей клиента для модального окна."""
        html = f"""
        <div>
            <div class="mb-3">
                <label class="form-label"><strong>ID:</strong></label>
                <div class="form-control-plaintext">{customer.customer_id}</div>
            </div>
            <div class="mb-3">
                <label class="form-label"><strong>Наименование:</strong></label>
                <div class="form-control-plaintext">{customer.name}</div>
            </div>
            <div class="mb-3">
                <label class="form-label"><strong>Адрес:</strong></label>
                <div class="form-control-plaintext">{customer.address}</div>
            </div>
            <div class="mb-3">
                <label class="form-label"><strong>Телефон:</strong></label>
                <div class="form-control-plaintext">{customer.phone}</div>
            </div>
            <div class="mb-3">
                <label class="form-label"><strong>Контактное лицо:</strong></label>
                <div class="form-control-plaintext">{customer.contact_person}</div>
            </div>
        </div>
        """
        return self._wrap_response(html, content_type='text/html; charset=utf-8')

    def render_json(self, data):
        """Рендер JSON ответа."""
        import json
        response_body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        return [
            '200 OK',
            [('Content-Type', 'application/json; charset=utf-8'),
             ('Content-Length', str(len(response_body)))],
            [response_body]
        ]

    def render_redirect(self, url):
        """Рендер редиректа."""
        return [
            '302 Found',
            [('Location', url),
             ('Content-Type', 'text/plain; charset=utf-8'),
             ('Content-Length', '0')],
            []
        ]

    def render_not_found(self):
        """Рендер страницы 404."""
        html = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>404 Not Found</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container mt-4">
                <div class="alert alert-danger">
                    <h1>404 - Страница не найдена</h1>
                    <p>Запрошенная страница не существует.</p>
                    <a href="/" class="btn btn-primary">Вернуться на главную</a>
                </div>
            </div>
        </body>
        </html>
        """
        return self._wrap_response(html, status='404 Not Found')

    def _wrap_response(self, html, status='200 OK', content_type='text/html; charset=utf-8'):
        """Обертка для HTTP ответа."""
        response_body = html.encode('utf-8')
        return [
            status,
            [('Content-Type', content_type),
             ('Content-Length', str(len(response_body)))],
            [response_body]
        ]