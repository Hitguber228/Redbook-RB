"""
Точка входа для запуска «Интерактивной красной книги Республики Беларусь».

Варианты запуска:
1. Десктопное приложение Windows:
   python run.py

2. Запуск в режиме Web / PWA (для тестирования на iPhone и Android в браузере):
   python run.py --web
"""

import sys
import os
import flet as ft
from src.main import main

def start_app(is_web: bool = False):
    app_runner = getattr(ft, "run", getattr(ft, "app", None))
    if not app_runner:
        raise RuntimeError("Не найден метод запуска приложения в установленной версии Flet")

    if is_web:
        port = 8550
        print(f"🚀 Запуск «Красной книги Беларуси» в режиме Web/PWA на http://localhost:{port}")
        app_runner(main, view=ft.AppView.WEB_BROWSER, port=port)
    else:
        print("🌲 Запуск «Красной книги Беларуси» в десктопном режиме Windows...")
        app_runner(main, view=ft.AppView.FLET_APP)

if __name__ == "__main__":
    is_web_mode = "--web" in sys.argv or "-w" in sys.argv
    start_app(is_web=is_web_mode)

