"""
Здесь описаны константы для Callback`ов
"""

TOGGLE_SETTINGS = "toggle_settings"
"""
Переключает параметр в настройках
"""

GET_HOMEWORK_MENU = "HOMEWORK_MENU"
"""
Открывает меню домашнего задания
"""

GET_HOMEWORK = "HOMEWORK"
"""
Получает домашнее задание
Использование: {CBT.GET_HOMEWORK}:{index}:{edit_message}

index: int - индекс дня недели начиная с 1 (1 - понедельник, 5 - пятница)
edit_message: int - Изменять сообщение? (1 - де, 0 - нет)
"""
