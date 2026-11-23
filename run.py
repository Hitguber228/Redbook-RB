"""
Точка входа для запуска «Интерактивной красной книги Республики Беларусь».

Варианты запуска:
1. Десктопное приложение Windows:
   python run.py

2. Запуск в режиме Web / PWA (для ПК и тестирования на iPhone / Android в браузере):
   python run.py --web

3. Запуск Web-сервера без автоматического открытия вкладки в браузере:
   python run.py --web --no-browser
"""

import sys
import os
import socket
import webbrowser
import flet as ft
from src.main import main

# Перехватываем открытие браузера, чтобы 0.0.0.0 на Windows всегда открывался как localhost
_real_webbrowser_open = webbrowser.open

def _safe_browser_open(url: str, *args, **kwargs):
    if "--no-browser" in sys.argv or "-n" in sys.argv:
        return True
    if isinstance(url, str) and "0.0.0.0" in url:
        url = url.replace("0.0.0.0", "localhost")
    return _real_webbrowser_open(url, *args, **kwargs)

# Патчим стандартный webbrowser и внутренний flet runner
webbrowser.open = _safe_browser_open
if hasattr(ft, "run") and hasattr(ft.run, "__globals__") and "open_in_browser" in ft.run.__globals__:
    def _safe_flet_open_in_browser(url: str):
        if "--no-browser" in sys.argv or "-n" in sys.argv:
            return
        if isinstance(url, str) and "0.0.0.0" in url:
            url = url.replace("0.0.0.0", "localhost")
        _real_webbrowser_open(url)
    ft.run.__globals__["open_in_browser"] = _safe_flet_open_in_browser


def get_local_ip() -> str:
    """
    Определяет реальный IP-адрес компьютера в локальной сети Wi-Fi/Ethernet,
    игнорируя виртуальные сетевые адаптеры (WSL, Docker 10.255.x.x, Hyper-V).
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()

        # Если попал виртуальный сетевой мост (WSL / Hyper-V)
        if ip.startswith("10.255.") or ip.startswith("172."):
            hostname = socket.gethostname()
            for info in socket.getaddrinfo(hostname, None, socket.AF_INET):
                cand = info[4][0]
                if cand.startswith("192.168.") or (cand.startswith("10.") and not cand.startswith("10.255.")):
                    return cand
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
        no_browser = "--no-browser" in sys.argv or "-n" in sys.argv

        print(f"\n========================================================")
        print(f"🌿 [WEB/PWA] Красная книга Беларуси успешно запущена:")
        print(f"   💻 Компьютер (браузер):     http://localhost:{port}")
        print(f"   📱 Смартфон (Wi-Fi):        http://{local_ip}:{port}")
        if no_browser:
            print(f"   ℹ️ Автооткрытие браузера отключено (--no-browser)")
        else:
            print(f"   🌐 Открываем http://localhost:{port} в браузере...")
        print(f"========================================================\n")

        app_runner(
            main,
            host="0.0.0.0",
            port=port,
            view=ft.AppView.WEB_BROWSER if not no_browser else None,
            assets_dir=assets_path
        )
    else:
        print("\n========================================================")
        print("💻 [DESKTOP] Запуск «Красной книги Беларуси» в окне Windows...")
        print("   (Для запуска в веб/на смартфоне используйте: python run.py --web)")
        print("========================================================\n")
        app_runner(main, view=ft.AppView.FLET_APP, assets_dir=assets_path)


if __name__ == "__main__":
    is_web_mode = "--web" in sys.argv or "-w" in sys.argv
    start_app(is_web=is_web_mode)
