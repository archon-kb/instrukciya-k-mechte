#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
polza_image.py — генератор изображений для сайта «Инструкция к мечте» через Polza.ai.

ЦЕЛЬ ФАЙЛА:
    Один аккуратный инструмент, который по текстовому описанию ("промпту") создаёт
    картинку нужной модели на сервисе Polza.ai, скачивает её в папку проекта и
    рядом кладёт «паспорт» картинки (manifest) — чем, по какому запросу и за сколько
    она сделана. Это нужно, чтобы любой ассет сайта был прослеживаемым: видно
    происхождение, можно повторить или пересоздать.

ЧТО НА ВХОДЕ:
    - переменная окружения POLZA_API_KEY (ключ доступа; в код не зашивается);
    - аргументы командной строки: описание картинки, модель, пропорции, разрешение,
      имя файла и папка назначения.

ЧТО НА ВЫХОДЕ:
    - один или несколько .png-файлов в папке назначения (по умолчанию assets/generated/);
    - файл <имя>.manifest.json с провенансом (запрос, модель, стоимость, ссылки, дата).

КАКОЙ РАЗДЕЛ РАБОТЫ ПОКРЫВАЕТ:
    Step 3 редизайна сайта (taste-skill, режим Overhaul) — генерация атмосферы героя и
    декоративных фактур «полевого определителя». Люди и пейзажи направлений на сайт
    идут реальными фото, а НЕ отсюда.

ЗАВИСИМОСТИ: только стандартная библиотека Python (urllib, json) — внешних пакетов нет.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

# Базовый адрес OpenAI-совместимого API Polza.ai и эндпоинт генерации медиа.
POLZA_BASE_URL: str = "https://api.polza.ai/api/v1"
MEDIA_ENDPOINT: str = f"{POLZA_BASE_URL}/media"


def прочитать_ключ_доступа() -> str:
    """Берёт ключ Polza.ai из окружения; при отсутствии — внятно падает.

    Ключ намеренно не хранится в коде и не печатается: он живёт в окружении
    (его подгружает вызывающая оболочка), а мы лишь читаем его значение.
    """
    ключ = os.environ.get("POLZA_API_KEY", "").strip()
    if not ключ:
        sys.exit(
            "ОШИБКА: переменная POLZA_API_KEY не задана в окружении.\n"
            "Подгрузи её перед запуском, например:\n"
            "  eval \"$(grep '^[[:space:]]*export[[:space:]]\\+POLZA_API_KEY=' ~/.zshrc | tail -1)\""
        )
    return ключ


def запросить_генерацию(
    ключ_доступа: str,
    промпт: str,
    модель: str,
    пропорции: str,
    разрешение: str,
    сколько_картинок: int,
) -> dict[str, Any]:
    """Отправляет на Polza.ai задачу на генерацию и возвращает разобранный JSON-ответ.

    Polza отвечает синхронно (status="completed") и кладёт ссылки на готовые картинки
    в поле data[].url. На случай асинхронного ответа (status="pending") вызывающий код
    умеет опросить задачу повторно (см. дождаться_готовности).
    """
    тело_запроса = {
        "model": модель,
        "input": {
            "prompt": промпт,
            "aspect_ratio": пропорции,
            "image_resolution": разрешение,
            "max_images": сколько_картинок,
        },
    }
    запрос = urllib.request.Request(
        MEDIA_ENDPOINT,
        data=json.dumps(тело_запроса).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {ключ_доступа}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(запрос, timeout=180) as ответ:
            return json.loads(ответ.read().decode("utf-8"))
    except urllib.error.HTTPError as ошибка:
        тело = ошибка.read().decode("utf-8", "replace")
        sys.exit(f"ОШИБКА API ({ошибка.code}): {тело}")
    except urllib.error.URLError as ошибка:
        sys.exit(f"ОШИБКА сети: {ошибка}")


def дождаться_готовности(ключ_доступа: str, задача: dict[str, Any]) -> dict[str, Any]:
    """Если задача вернулась незавершённой — опрашивает её до готовности.

    Для текущих image-моделей Polza ответ приходит сразу готовым, поэтому в типичном
    случае цикл не выполняется ни разу. Подстраховка на будущее (видео/тяжёлые модели).
    """
    статус = задача.get("status")
    идентификатор = задача.get("id")
    попыток = 0
    while статус == "pending" and идентификатор and попыток < 30:
        time.sleep(2)
        попыток += 1
        запрос = urllib.request.Request(
            f"{MEDIA_ENDPOINT}/{идентификатор}",
            headers={"Authorization": f"Bearer {ключ_доступа}"},
        )
        try:
            with urllib.request.urlopen(запрос, timeout=60) as ответ:
                задача = json.loads(ответ.read().decode("utf-8"))
                статус = задача.get("status")
        except urllib.error.URLError:
            break
    return задача


def скачать_файл(ссылка: str, путь_назначения: str) -> None:
    """Качает картинку по ссылке (CDN Polza временный) в постоянный файл проекта."""
    with urllib.request.urlopen(ссылка, timeout=120) as поток:
        данные = поток.read()
    with open(путь_назначения, "wb") as файл:
        файл.write(данные)


def сгенерировать_и_сохранить(аргументы: argparse.Namespace) -> None:
    """Основной сценарий: запросить картинку(и), скачать, записать паспорт-манифест."""
    ключ = прочитать_ключ_доступа()
    os.makedirs(аргументы.out, exist_ok=True)

    задача = запросить_генерацию(
        ключ_доступа=ключ,
        промпт=аргументы.prompt,
        модель=аргументы.model,
        пропорции=аргументы.aspect,
        разрешение=аргументы.resolution,
        сколько_картинок=аргументы.max_images,
    )
    задача = дождаться_готовности(ключ, задача)

    список_картинок = задача.get("data") or []
    if not список_картинок:
        sys.exit(f"ОШИБКА: ответ без картинок. Полный ответ: {json.dumps(задача, ensure_ascii=False)}")

    сохранённые_файлы: list[str] = []
    for номер, картинка in enumerate(список_картинок, start=1):
        ссылка = картинка.get("url")
        if not ссылка:
            continue
        суффикс = "" if len(список_картинок) == 1 else f"_{номер}"
        имя_файла = f"{аргументы.name}{суффикс}.png"
        полный_путь = os.path.join(аргументы.out, имя_файла)
        скачать_файл(ссылка, полный_путь)
        сохранённые_файлы.append(полный_путь)

    # «Паспорт» ассета — провенанс для прослеживаемости (CLAUDE.md: трассируемость истины).
    стоимость = (задача.get("usage") or {}).get("cost_rub")
    манифест = {
        "name": аргументы.name,
        "prompt": аргументы.prompt,
        "model": аргументы.model,
        "aspect_ratio": аргументы.aspect,
        "image_resolution": аргументы.resolution,
        "cost_rub": стоимость,
        "source_urls": [к.get("url") for к in список_картинок],
        "files": сохранённые_файлы,
        "generation_id": задача.get("id"),
        "created_unix": задача.get("created"),
    }
    путь_манифеста = os.path.join(аргументы.out, f"{аргументы.name}.manifest.json")
    with open(путь_манифеста, "w", encoding="utf-8") as файл:
        json.dump(манифест, файл, ensure_ascii=False, indent=2)

    print(f"OK: сохранено {len(сохранённые_файлы)} файл(ов), стоимость {стоимость} ₽")
    for путь in сохранённые_файлы:
        print(f"  - {путь}")
    print(f"  паспорт: {путь_манифеста}")


def разобрать_аргументы() -> argparse.Namespace:
    """Описывает аргументы командной строки инструмента."""
    парсер = argparse.ArgumentParser(description="Генерация картинки через Polza.ai")
    парсер.add_argument("--prompt", required=True, help="Текстовое описание картинки")
    парсер.add_argument("--name", required=True, help="Базовое имя файла (без расширения)")
    парсер.add_argument(
        "--out",
        default=os.path.join(os.path.dirname(__file__), "..", "site-mockup", "assets", "generated"),
        help="Папка назначения (по умолчанию site-mockup/assets/generated/)",
    )
    парсер.add_argument("--model", default="black-forest-labs/flux.2-flex", help="ID модели Polza")
    парсер.add_argument("--aspect", default="16:9", help="Пропорции: 1:1, 4:3, 3:4, 16:9, 9:16, 3:2, 2:3")
    парсер.add_argument("--resolution", default="1K", help="Разрешение: 1K или 2K")
    парсер.add_argument("--max-images", dest="max_images", type=int, default=1, help="Сколько картинок (1-8)")
    return парсер.parse_args()


if __name__ == "__main__":
    сгенерировать_и_сохранить(разобрать_аргументы())
