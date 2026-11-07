"""
Утилиты и вспомогательные функции для приложения «Красная книга Беларуси».
"""

import os
import webbrowser
from typing import Optional
import flet as ft


def open_target(target: str, page: Optional[ft.Page] = None) -> bool:
    """
    Универсальное и надежное открытие веб-страниц, интерактивной карты Leaflet
    и внешних ссылок как в десктопном режиме Windows, так и в браузере.
    """
    if not target:
        return False

    # 1. Если это относительный путь к локальным ресурсам (например, /map/index.html)
    if not (target.startswith("http://") or target.startswith("https://") or target.startswith("file://")):
        clean_rel = target.lstrip("/\\")
        base_assets = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
        file_path = os.path.join(base_assets, clean_rel)
        if os.path.exists(file_path):
            target_uri = f"file:///{file_path.replace(os.sep, '/')}"
        else:
            target_uri = target
    else:
        target_uri = target

    # 2. Если запуск в веб-режиме Flet
    if page and getattr(page, "web", False):
        try:
            import asyncio
            web_target = target if (target.startswith("/") or target.startswith("http")) else target_uri
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(ft.UrlLauncher().launch_url(web_target))
                return True
            except RuntimeError:
                pass
        except Exception as e:
            print(f"[open_target web error] {e}")

    # 3. Десктопный режим Windows (открывает системный браузер Edge/Chrome без лагов)
    try:
        webbrowser.open(target_uri)
        return True
    except Exception as err:
        print(f"[open_target desktop error] {err}")
        return False
