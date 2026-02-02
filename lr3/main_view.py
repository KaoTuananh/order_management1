from models.observer import Observer
import urllib.parse


class MainView(Observer):
    """Главное представление с поддержкой Observer."""

    def render_index(self, customers, page, total_pages, sort_by=None, reverse=False,
                     filter_type='name', filter_name=None, filter_phone=None,
                     filter_address=None, sort_links=None):
        """Рендер главной страницы с фильтрацией."""

        # Устанавливаем значения для полей фильтрации
        name_value = filter_name if filter_type == 'name' and filter_name else ""
        phone_value = filter_phone if filter_type == 'phone' and filter_phone else ""
        address_value = filter_address if filter_type == 'address' and filter_address else ""

        # Определяем активный тип фильтра
        name_active = "active" if filter_type == 'name' else ""
        phone_active = "active" if filter_type == 'phone' else ""
        address_active = "active" if filter_type == 'address' else ""

        # Информация о фильтрации
        filter_info = ""
        if filter_type == 'name' and filter_name:
            filter_info = f'<div class="alert alert-info mb-3">Фильтр: <strong>по имени</strong> - "{filter_name}"</div>'
        elif filter_type == 'phone' and filter_phone:
            filter_info = f'<div class="alert alert-info mb-3">Фильтр: <strong>по телефону</strong> - "{filter_phone}"</div>'
        elif filter_type == 'address' and filter_address:
            filter_info = f'<div class="alert alert-info mb-3">Фильтр: <strong>по адресу</strong> - "{filter_address}"</div>'

        html = f"""
        <!-- HTML код с формой фильтрации -->
        <div class="card mb-4">
            <div class="card-header">
                <h5 class="mb-0">Фильтрация и сортировка</h5>
            </div>
            <div class="card-body">
                <form action="/filter" method="GET" class="row g-3">
                    <input type="hidden" name="filter_type" id="filterType" value="{filter_type}">

                    <div class="col-md-3">
                        <div class="btn-group w-100" role="group">
                            <button type="button" class="btn {name_active}" onclick="setFilterType('name')">По имени</button>
                            <button type="button" class="btn {phone_active}" onclick="setFilterType('phone')">По телефону</button>
                            <button type="button" class="btn {address_active}" onclick="setFilterType('address')">По адресу</button>
                        </div>
                    </div>

                    <div class="col-md-6">
                        <div id="nameFilter" class="filter-field" style="display: {'block' if filter_type == 'name' else 'none'};">
                            <input type="text" class="form-control" name="name" placeholder="Введите имя для фильтрации" value="{name_value}">
                        </div>
                        <div id="phoneFilter" class="filter-field" style="display: {'block' if filter_type == 'phone' else 'none'};">
                            <input type="text" class="form-control" name="phone" placeholder="Введите телефон для фильтрации" value="{phone_value}">
                        </div>
                        <div id="addressFilter" class="filter-field" style="display: {'block' if filter_type == 'address' else 'none'};">
                            <input type="text" class="form-control" name="address" placeholder="Введите адрес для фильтрации" value="{address_value}">
                        </div>
                    </div>

                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary w-100">Применить фильтр</button>
                        <a href="/" class="btn btn-secondary w-100 mt-2">Сбросить фильтр</a>
                    </div>
                </form>
            </div>
        </div>
        """
        return self._wrap_response(html)