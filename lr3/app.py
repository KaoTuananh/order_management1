#!/usr/bin/env python3
"""
Лабораторная работа 3: Веб-сервер для управления клиентами
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from controllers.main_controller import MainController


class Application:
    """WSGI приложение для управления клиентами."""

    def __init__(self):
        self.main_controller = MainController()

    def __call__(self, environ, start_response):
        """Обработка WSGI запросов."""
        path = environ.get('PATH_INFO', '/')

        # Маршрутизация
        if path == '/' or path == '/index':
            response = self.main_controller.handle_request(environ)
        elif path == '/filter':  # РОУТ ДЛЯ ФИЛЬТРАЦИИ
            response = self.main_controller.handle_request(environ)
