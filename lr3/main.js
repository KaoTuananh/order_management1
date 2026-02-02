// Основной JavaScript для приложения
let updateCounter = 0;

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 1050; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);

    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function formatPhoneNumber(phone) {
    let cleaned = phone.replace(/\D/g, '');

    if (cleaned.length === 10) {
        return '+7 (' + cleaned.substring(0, 3) + ') ' + cleaned.substring(3, 6) + '-' + cleaned.substring(6, 8) + '-' + cleaned.substring(8, 10);
    } else if (cleaned.length === 11) {
        return '+' + cleaned.charAt(0) + ' (' + cleaned.substring(1, 4) + ') ' + cleaned.substring(4, 7) + '-' + cleaned.substring(7, 9) + '-' + cleaned.substring(9, 11);
    }

    return phone;
}

// Обработка сообщений от дочерних окон (для паттерна Observer)
window.addEventListener('message', function(event) {
    if (event.data && event.data.action === 'customer_details_opened') {
        console.log(`Получено сообщение об открытии деталей клиента #${event.data.customer_id}`);
        showNotification(`Детали клиента #${event.data.customer_id} открыты в отдельной вкладке`);
    } else if (event.data && event.data.action === 'customer_updated') {  // ДОБАВЛЕНО
        console.log('Получено сообщение об обновлении клиента');
        showNotification('Данные клиента обновлены через паттерн Наблюдатель');

        // Обновляем страницу через 1 секунду
        setTimeout(() => {
            location.reload();
        }, 1000);
    }
});

// Инициализация счетчика обновлений Observer
document.addEventListener('DOMContentLoaded', function() {
    // Подсветка строк таблицы при наведении
    const tableRows = document.querySelectorAll('table tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.classList.add('table-active');
        });
        row.addEventListener('mouseleave', function() {
            this.classList.remove('table-active');
        });
    });

    // Инициализация счетчика обновлений Observer
    const counterElement = document.getElementById('updateCounter');
    if (counterElement) {
        // Получаем реальные обновления с сервера
        setInterval(() => {
            fetch('/get_update_count')
                .then(response => response.json())
                .then(data => {
                    if (data.update_count) {
                        updateCounter = data.update_count;
                        counterElement.textContent = updateCounter;
                    }
                })
                .catch(error => {
                    console.error('Error fetching update count:', error);
                });
        }, 3000); // Каждые 3 секунды проверяем обновления
    }
});