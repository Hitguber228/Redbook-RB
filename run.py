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
import socket
import flet as ft
from src.main import main

def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def start_app(is_web: bool = False):
    app_runner = getattr(ft, "run", getattr(ft, "app", None))
    if not app_runner:
        raise RuntimeError("Не найден метод запуска приложения в установленной версии Flet")

    assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets"))

    if is_web:
        port = 8550
        local_ip = get_local_ip()
        print(f"[WEB] Запуск «Красной книги Беларуси» в режиме Web/PWA:")
        print(f"   [ПК] На этом компьютере: http://localhost:{port}")
        print(f"   [СМАРТФОН] На iPhone / Android в той же сети Wi-Fi: http://{local_ip}:{port}")
        print(f"   [ИНФО] На iPhone: откройте ссылку в Safari -> нажмите «Поделиться» -> «На экран Домой»\n")
        app_runner(
            main,
            host="0.0.0.0",
            port=port,
            view=ft.AppView.WEB_BROWSER,
            assets_dir=assets_path
        )
    else:
        print("[DESKTOP] Запуск «Красной книги Беларуси» в десктопном режиме Windows...")
        app_runner(main, view=ft.AppView.FLET_APP, assets_dir=assets_path)

if __name__ == "__main__":
    is_web_mode = "--web" in sys.argv or "-w" in sys.argv
    start_app(is_web=is_web_mode)

