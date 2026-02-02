#!/usr/bin/env python3
"""
Лабораторная работа 3: Веб-сервер для управления клиентами
Архитектура MVC без фреймворков с паттерном Наблюдатель
"""

import os
import sys

# Добавляем пути к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.main_controller import MainController
from controllers.customer_form_controller import CustomerFormController  # ИМПОРТ ДОБАВЛЕН


class Application:
    """WSGI приложение для управления клиентами."""

    def __init__(self):
        self.main_controller = MainController()

    def __call__(self, environ, start_response):
        """Обработка WSGI запросов."""
        path = environ.get('PATH_INFO', '/')

        # Статические файлы
        if path.startswith('/static/'):
            return self.serve_static(environ, start_response)

        # Маршрутизация
        if path == '/' or path == '/index':
            response = self.main_controller.handle_request(environ)
        elif path == '/get_customer_details':
            response = self.main_controller.handle_request(environ)
        elif path == '/add':  # НОВЫЙ МАРШРУТ ДОБАВЛЕН
            # Контроллер для добавления
            controller = CustomerFormController(self.main_controller.repository, 'add')
            response = controller.handle_request(environ)
        elif path == '/get_update_count':
            response = self.main_controller.handle_request(environ)
        else:
            # Проверяем, не запрашивают ли статический файл без префикса
            if '.' in path:
                return self.serve_static(environ, start_response)
            status = '404 Not Found'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            body = b'<h1>404 Not Found</h1><a href="/">Go Home</a>'
            start_response(status, headers)
            return [body]

        # Вызываем start_response и возвращаем тело ответа
        start_response(response[0], response[1])
        return response[2]

    def serve_static(self, environ, start_response):
        """Обслуживание статических файлов."""
        path = environ['PATH_INFO']

        # Определяем путь к статическим файлам
        if path.startswith('/static/'):
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
            file_path = os.path.join(static_dir, path[8:])  # Убираем '/static/'
        else:
            # Пробуем найти файл в статической папке
            static_dir = os.path.join(os.path.dirname(__file__), 'static')
            file_path = os.path.join(static_dir, path.lstrip('/'))

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            status = '404 Not Found'
            headers = [('Content-Type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [b'File not found']

        # Определяем Content-Type
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.html': 'text/html',
            '.txt': 'text/plain'
        }

        ext = os.path.splitext(file_path)[1].lower()
        content_type = content_types.get(ext, 'application/octet-stream')

        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            status = '200 OK'
            headers = [
                ('Content-Type', content_type),
                ('Content-Length', str(len(content)))
            ]
            start_response(status, headers)
            return [content]
        except Exception as e:
            status = '500 Internal Server Error'
            headers = [('Content-Type', 'text/plain; charset=utf-8')]
            start_response(status, headers)
            return [str(e).encode()]


def run_server(host='localhost', port=8000):
    """Запуск веб-сервера."""
    from wsgiref.simple_server import make_server

    app = Application()

    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА 3: Веб-сервер для управления клиентами")
    print("=" * 60)
    print(f"Сервер запущен на http://{host}:{port}")
    print("\nАрхитектура MVC с паттерном Наблюдатель:")
    print("- Модели: customer.py, customer_repository.py")
    print("- Представления: main_view.py, customer_details_view.py, customer_form_view.py")
    print("- Контроллеры: main_controller.py, customer_form_controller.py")
    print("\nДоступные маршруты:")
    print("  GET  /                    - Главная страница с таблицей клиентов")
    print("  GET  /get_customer_details?id=<id> - Детальная информация о клиенте (отдельная вкладка)")
    print("  GET  /add                 - Добавление клиента")
    print("  POST /add                 - Отправка формы добавления")
    print("\nОсобенности реализации:")
    print("  ✓ Паттерн Наблюдатель (Observer/Observable)")
    print("  ✓ Валидация данных согласно ЛР1 (телефон 5-20 цифр)")
    print("  ✓ Просмотр деталей в отдельной вкладке")
    print("  ✓ Добавление клиентов через отдельную форму")
    print("=" * 60)
    print("Нажмите Ctrl+C для остановки сервера")

    try:
        server = make_server(host, port, app)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nСервер остановлен")
    except Exception as e:
        print(f"Ошибка при запуске сервера: {e}")


if __name__ == '__main__':
    run_server()