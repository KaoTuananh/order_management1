from models.observer import Observer
import urllib.parse


class MainView(Observer):
    """Главное представление с поддержкой Observer."""

    def render_index(self, customers, page, total_pages, sort_by=None, reverse=False,
                     filter_type='name', filter_name=None, filter_phone=None,
                     filter_address=None, sort_links=None):
        """Рендер главной страницы с сортировкой."""

        # Информация о сортировке
        sort_info = ""
        if sort_by:
            sort_direction = "по убыванию" if reverse else "по возрастанию"
            field_names = {
                'customer_id': 'ID',
                'name': 'имени',
                'phone': 'телефону',
                'address': 'адресу',
                'contact_person': 'контактному лицу'
            }
            if sort_by in field_names:
                sort_info = f'<div class="alert alert-warning mb-3">Сортировка: <strong>{field_names[sort_by]}</strong> ({sort_direction})</div>'

        # В таблице добавляем индикаторы сортировки
        headers = {
            'customer_id': 'ID',
            'name': 'Имя',
            'phone': 'Телефон',
            'contact_person': 'Контактное лицо',
            'actions': 'Действия'
        }

        # Генерируем заголовки с иконками сортировки
        headers_html = ""
        for field, title in headers.items():
            if field == 'actions':
                headers_html += f'<th>{title}</th>'
            else:
                sort_icon = ""
                if field == sort_by:  # ИНДИКАТОР АКТИВНОЙ СОРТИРОВКИ
                    sort_icon = " 🔽" if reverse else " 🔼"
                sort_url = sort_links.get(field, f'/?sort={field}&reverse=false')

                headers_html += f'<th><a href="{sort_url}" style="text-decoration: none; color: inherit; display: flex; align-items: center; justify-content: space-between;">{title}<span>{sort_icon}</span></a></th>'

        html = f"""
        <!-- HTML код с сортировкой -->
        {sort_info}

        <div class="mt-3">
            <small class="text-muted">Быстрая сортировка:</small>
            <div class="btn-group mt-1" role="group">
                <a href="{sort_links.get('customer_id', '/?sort=customer_id')}" class="btn btn-outline-secondary btn-sm">По ID</a>
                <a href="{sort_links.get('name', '/?sort=name')}" class="btn btn-outline-secondary btn-sm">По имени</a>
                <a href="{sort_links.get('phone', '/?sort=phone')}" class="btn btn-outline-secondary btn-sm">По телефону</a>
                <a href="{sort_links.get('address', '/?sort=address')}" class="btn btn-outline-secondary btn-sm">По адресу</a>
                <a href="{sort_links.get('contact_person', '/?sort=contact_person')}" class="btn btn-outline-secondary btn-sm">По конт. лицу</a>
            </div>
        </div>

        <table class="table table-striped table-hover">
            <thead>
                <tr>
                    {headers_html}  <!-- ЗАГОЛОВКИ С ССЫЛКАМИ ДЛЯ СОРТИРОВКИ -->
                </tr>
            </thead>
            <tbody>
                <!-- Данные с сортировкой -->
            </tbody>
        </table>
        """
        return self._wrap_response(html)