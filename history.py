"""
history.py — логика сохранения и загрузки истории цитат в/из JSON.
"""

import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history() -> list:
    """
    Загружает историю из файла history.json.
    Возвращает список записей вида {text, author, topic, timestamp}.
    Если файл не существует или повреждён — возвращает пустой список.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history: list) -> None:
    """
    Сохраняет историю цитат в файл history.json.
    history — список записей вида {text, author, topic, timestamp}.
    """
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[history] Ошибка при сохранении: {e}")


def make_entry(text: str, author: str, topic: str) -> dict:
    """Создаёт запись истории с текущей меткой времени."""
    return {
        "text": text,
        "author": author,
        "topic": topic,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
