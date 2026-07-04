#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
polza_media.py — медиа-инструмент Polza.ai для сайта «Инструкция к мечте».

ЦЕЛЬ ФАЙЛА:
    Универсальный генератор/редактор медиа через Polza.ai: text→картинка,
    картинка+текст→картинка (правка: убрать фон, дорисовать), и картинка→видео
    (оживление). Скачивает результат в проект и кладёт рядом «паспорт» (manifest)
    с провенансом. Расширяет polza_image.py входными картинками и видео-режимом.

ЧТО НА ВХОДЕ:
    - переменная окружения POLZA_API_KEY (ключ; в код не зашит, не печатается);
    - аргументы: режим (image/video), модель, описание, входные картинки (для правки/
      оживления), пропорции, разрешение, длительность (для видео), имя и папка вывода.

ЧТО НА ВЫХОДЕ:
    - .png (картинка) или .mp4 (видео) в папке назначения;
    - <имя>.manifest.json с провенансом (запрос, модель, стоимость, ссылки, дата).

КАКОЙ РАЗДЕЛ РАБОТЫ ПОКРЫВАЕТ:
    Step 3 редизайна (гибрид-анимация героя): вырезание гор из сгенерированной
    картинки (правка → прозрачный слой), генерация облаков-видео, оживление элементов.

ЗАВИСИМОСТИ: только стандартная библиотека (urllib, json, base64).
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any

POLZA_BASE_URL: str = "https://api.polza.ai/api/v1"
MEDIA_ENDPOINT: str = f"{POLZA_BASE_URL}/media"


def прочитать_ключ_доступа() -> str:
    """Берёт ключ Polza.ai из окружения; при отсутствии — внятно падает (значение не печатает)."""
    ключ = os.environ.get("POLZA_API_KEY", "").strip()
    if not ключ:
        sys.exit("ОШИБКА: POLZA_API_KEY не задан в окружении.")
    return ключ


def файл_в_data_uri(путь: str) -> str:
    """Кодирует локальную картинку в data-URI base64 — так Polza принимает вход (он не видит локальные пути)."""
    расширение = os.path.splitext(путь)[1].lower().lstrip(".") or "png"
    mime = "jpeg" if расширение in ("jpg", "jpeg") else расширение
    with open(путь, "rb") as файл:
        кодированное = base64.b64encode(файл.read()).decode("ascii")
    return f"data:image/{mime};base64,{кодированное}"


def отправить_задачу(ключ_доступа: str, модель: str, вход: dict[str, Any]) -> dict[str, Any]:
    """POST задачи генерации/правки/оживления; возвращает разобранный JSON-ответ."""
    тело = {"model": модель, "input": вход}
    запрос = urllib.request.Request(
        MEDIA_ENDPOINT,
        data=json.dumps(тело).encode("utf-8"),
        headers={"Authorization": f"Bearer {ключ_доступа}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(запрос, timeout=240) as ответ:
            return json.loads(ответ.read().decode("utf-8"))
    except urllib.error.HTTPError as ошибка:
        sys.exit(f"ОШИБКА API ({ошибка.code}): {ошибка.read().decode('utf-8', 'replace')}")
    except urllib.error.URLError as ошибка:
        sys.exit(f"ОШИБКА сети: {ошибка}")


def дождаться_готовности(ключ_доступа: str, задача: dict[str, Any], максимум_секунд: int = 300) -> dict[str, Any]:
    """Опрашивает задачу до статуса completed (видео делается не мгновенно)."""
    идентификатор = задача.get("id")
    прошло = 0
    while задача.get("status") in ("pending", "processing", "queued", "running") and идентификатор and прошло < максимум_секунд:
        time.sleep(4)
        прошло += 4
        запрос = urllib.request.Request(
            f"{MEDIA_ENDPOINT}/{идентификатор}",
            headers={"Authorization": f"Bearer {ключ_доступа}"},
        )
        try:
            with urllib.request.urlopen(запрос, timeout=60) as ответ:
                задача = json.loads(ответ.read().decode("utf-8"))
        except urllib.error.URLError:
            break
    return задача


def скачать(ссылка: str, путь: str) -> None:
    """Качает результат (CDN Polza временный) в постоянный файл проекта."""
    with urllib.request.urlopen(ссылка, timeout=240) as поток:
        данные = поток.read()
    with open(путь, "wb") as файл:
        файл.write(данные)


def расширение_по_ссылке(ссылка: str, режим: str) -> str:
    """Определяет расширение файла по URL, с дефолтом по режиму."""
    низ = ссылка.lower().split("?")[0]
    for ext in (".mp4", ".webm", ".mov", ".png", ".jpg", ".jpeg", ".webp"):
        if низ.endswith(ext):
            return ext
    return ".mp4" if режим == "video" else ".png"


def выполнить(аргументы: argparse.Namespace) -> None:
    """Основной сценарий: собрать input, отправить, дождаться, скачать, записать паспорт."""
    ключ = прочитать_ключ_доступа()
    os.makedirs(аргументы.out, exist_ok=True)

    вход: dict[str, Any] = {"prompt": аргументы.prompt}
    if аргументы.image:
        вход["images"] = [{"type": "base64", "data": файл_в_data_uri(п)} for п in аргументы.image]
    if аргументы.mode == "video":
        if аргументы.duration:
            вход["duration"] = аргументы.duration
        if аргументы.resolution:
            вход["resolution"] = аргументы.resolution
    else:
        if аргументы.aspect:
            вход["aspect_ratio"] = аргументы.aspect
        if аргументы.image_resolution:
            вход["image_resolution"] = аргументы.image_resolution

    задача = отправить_задачу(ключ, аргументы.model, вход)
    задача = дождаться_готовности(ключ, задача)
    данные = задача.get("data") or []
    if not данные:
        sys.exit(f"ОШИБКА: нет результата. Ответ: {json.dumps(задача, ensure_ascii=False)[:600]}")

    сохранённые: list[str] = []
    for номер, элемент in enumerate(данные, start=1):
        ссылка = элемент.get("url")
        if not ссылка:
            continue
        суффикс = "" if len(данные) == 1 else f"_{номер}"
        путь = os.path.join(аргументы.out, f"{аргументы.name}{суффикс}{расширение_по_ссылке(ссылка, аргументы.mode)}")
        скачать(ссылка, путь)
        сохранённые.append(путь)

    стоимость = (задача.get("usage") or {}).get("cost_rub")
    манифест = {
        "name": аргументы.name, "mode": аргументы.mode, "model": аргументы.model,
        "prompt": аргументы.prompt, "inputs": аргументы.image or [],
        "cost_rub": стоимость, "source_urls": [э.get("url") for э in данные],
        "files": сохранённые, "generation_id": задача.get("id"), "status": задача.get("status"),
    }
    with open(os.path.join(аргументы.out, f"{аргументы.name}.manifest.json"), "w", encoding="utf-8") as ф:
        json.dump(манифест, ф, ensure_ascii=False, indent=2)

    print(f"OK [{аргументы.mode}]: {len(сохранённые)} файл(ов), стоимость {стоимость} ₽, статус {задача.get('status')}")
    for п in сохранённые:
        print(f"  - {п}")


def разобрать_аргументы() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Polza.ai: генерация/правка картинок и видео")
    p.add_argument("--mode", choices=["image", "video"], default="image")
    p.add_argument("--prompt", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--image", action="append", help="Входная картинка (можно несколько раз) — для правки/оживления")
    p.add_argument("--out", default=os.path.join(os.path.dirname(__file__), "..", "site-mockup", "assets", "generated"))
    p.add_argument("--model", default="black-forest-labs/flux.2-flex")
    p.add_argument("--aspect", default="16:9")
    p.add_argument("--image-resolution", dest="image_resolution", default="1K")
    p.add_argument("--duration", default=None, help="Длительность видео, напр. 4s / 5s")
    p.add_argument("--resolution", default=None, help="Разрешение видео: 480p/720p/1080p")
    return p.parse_args()


if __name__ == "__main__":
    выполнить(разобрать_аргументы())
