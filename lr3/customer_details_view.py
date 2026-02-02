class CustomerDetailsView:
    """Представление для просмотра деталей клиента."""

    def __init__(self, controller):
        self.controller = controller

    def render_details(self, customer):
        """Рендер страницы с деталями клиента."""
        html = f"""
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Детали клиента #{customer.customer_id}</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="/static/css/style.css">
            <style>
                .container {{
                    max-width: 800px;
                    margin-top: 30px;
                }}
                .detail-card {{
                    margin-bottom: 20px;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    background-color: white;
                }}
                .detail-label {{
                    font-weight: bold;
                    color: #495057;
                    margin-bottom: 5px;
                }}
                .detail-value {{
                    font-size: 1.1em;
                    color: #212529;
                    padding: 10px;
                    background-color: #f8f9fa;
                    border-radius: 5px;
                    margin-bottom: 15px;
                }}
                .action-buttons {{
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="mb-4">Детальная информация о клиенте</h1>

                <div class="detail-card">
                    <div class="detail-label">ID клиента:</div>
                    <div class="detail-value">{customer.customer_id}</div>

                    <div class="detail-label">Наименование организации:</div>
                    <div class="detail-value">{customer.name}</div>

                    <div class="detail-label">Контактное лицо:</div>
                    <div class="detail-value">{customer.contact_person}</div>

                    <div class="detail-label">Телефон:</div>
                    <div class="detail-value">
                        <a href="tel:{customer.phone}" class="text-decoration-none">
                            {customer.phone}
                        </a>
                    </div>

                    <div class="detail-label">Адрес:</div>
                    <div class="detail-value">{customer.address}</div>

                    <div class="detail-label">Краткая информация:</div>
                    <div class="detail-value">
                        <code>{customer.display_short()}</code>
                    </div>
                </div>

                <div class="action-buttons">
                    <div class="row">
                        <div class="col-md-6 mb-2">
                            <a href="/edit?id={customer.customer_id}" class="btn btn-warning w-100">
                                Редактировать клиента
                            </a>
                        </div>
                    </div>
                </div>

                <div class="mt-4">
                    <a href="/" class="btn btn-secondary">
                        Вернуться к списку
                    </a>
                </div>
            </div>

            <script>
            // При открытии в новой вкладке обновляем родительское окно через Observer
            window.onload = function() {{
                try {{
                    if (window.opener && !window.opener.closed) {{
                        window.opener.postMessage({{
                            action: 'customer_details_opened', 
                            customer_id: {customer.customer_id}
                        }}, '*');
                    }}
                }} catch (e) {{
                    console.log('Не удалось отправить сообщение в родительское окно:', e);
                }}
            }};

            // Обработка сообщений Observer
            window.addEventListener('message', function(event) {{
                if (event.data && event.data.action === 'customer_updated') {{
                    console.log('Получено сообщение об обновлении клиента');
                    alert('Данные клиента обновлены. Страница будет перезагружена.');
                    location.reload();
                }}
            }});
            </script>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
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
            <link rel="stylesheet" href="/static/css/style.css">
        </head>
        <body>
            <div class="container mt-4">
                <div class="alert alert-danger">
                    <h4>Ошибка!</h4>
                    <p>{message}</p>
                    <div class="mt-3">
                        <a href="/" class="btn btn-primary">На главную</a>
                        <button onclick="window.history.back()" class="btn btn-secondary">Назад</button>
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