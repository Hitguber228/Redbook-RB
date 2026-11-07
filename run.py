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

if __name__ == "__main__":
    is_web = "--web" in sys.argv or "-w" in sys.argv

    if is_web:
        port = 8550
        print(f"🚀 Запуск «Красной книги Беларуси» в режиме Web/PWA на http://localhost:{port}")
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            port=port
        )
    else:
        print("🌲 Запуск «Красной книги Беларуси» в десктопном режиме Windows...")
        ft.app(
            target=main,
            view=ft.AppView.FLET_APP
        )
