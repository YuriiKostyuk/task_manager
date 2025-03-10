"""
Модуль инициализации маршрутизаторов приложения.

Этот модуль отвечает за регистрацию маршрутов и определение
структуры API приложения. Здесь собираются все маршрутизаторы
(routers), которые обрабатывают запросы и обеспечивают обработку
различных эндпоинтов.

Основные функции:
- Регистрация маршрутов для различных частей приложения.
- Объединение маршрутизаторов для удобства и организации кода.
- Определение зависимостей и обработчиков запросов.

Импортируемые модули:
- Разные модули маршрутов из приложения, включая (но не ограничиваясь) `tasks`, `users` и 'auth'.

"""
