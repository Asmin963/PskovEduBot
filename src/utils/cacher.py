import os
import json
from typing import Any, Dict

CACHE_FILE = '../../storage/cache'

def load_cache() -> Dict[str, Any]:
    """
    Загружает кеш из файла.

    :return: Словарь с кешем.
    """
    if not os.path.exists(CACHE_FILE):
        return {}

    with open(CACHE_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return {}

def save_cache(cache: Dict[str, Any]) -> None:
    """
    Сохраняет кеш в файл.

    :param cache: Словарь с кешем.
    """
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, 'w') as file:
        json.dump(cache, file, indent=4)

def add_to_cache(key: str, value: Any) -> None:
    """
    Добавляет элемент в кеш.

    :param key: Ключ (UUID).
    :param value: Значение (JSON данные).
    """
    cache = load_cache()
    cache[key] = value
    save_cache(cache)

def get_from_cache(key: str) -> Any:
    """
    Получает элемент из кеша по ключу.

    :param key: Ключ (UUID).
    :return: Значение (JSON данные) или None, если ключ не найден.
    """
    cache = load_cache()
    return cache.get(key)

def remove_from_cache(key: str) -> None:
    """
    Удаляет элемент из кеша по ключу.

    :param key: Ключ (UUID).
    """
    cache = load_cache()
    if key in cache:
        del cache[key]
        save_cache(cache)

def clear_cache() -> None:
    """
    Очищает кеш.
    """
    save_cache({})