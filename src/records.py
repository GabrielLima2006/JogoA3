"""Recordes por capítulo, guardados em saves/records.json."""

import json
import os

from .progress import SAVE_DIR

RECORDS_PATH = os.path.join(SAVE_DIR, "records.json")
GRADE_ORDER = {"S": 0, "A": 1, "B": 2, "C": 3}


def load_records(path=None):
    try:
        with open(path or RECORDS_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return [r for r in data if isinstance(r, dict)]
    except (OSError, ValueError):
        return []


def add_record(record, path=None):
    """record: {capitulo, protagonista, dificuldade, tempo, quedas, cartas, nota, pontos, data}"""
    path = path or RECORDS_PATH
    records = load_records(path)
    records.append(record)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=1)
    except OSError:
        pass
    return records


def best_records(records, limit=8):
    return sorted(records, key=lambda r: (GRADE_ORDER.get(r.get("nota"), 9), r.get("tempo", 1e9)))[:limit]
