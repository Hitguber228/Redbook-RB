import os
import pytest
from src.utils import open_target

def test_open_target_empty():
    assert open_target("") is False
    assert open_target(None) is False

def test_open_target_path_resolution(monkeypatch):
    opened_urls = []
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", lambda url: opened_urls.append(url) or True)

    # Relative map target
    success = open_target("/map/index.html")
    assert success is True
    assert len(opened_urls) == 1
    assert "file:///" in opened_urls[0]
    assert opened_urls[0].endswith("assets/map/index.html")

def test_open_target_external_url(monkeypatch):
    opened_urls = []
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", lambda url: opened_urls.append(url) or True)

    url = "https://example.com/audio.mp3"
    success = open_target(url)
    assert success is True
    assert len(opened_urls) == 1
    assert opened_urls[0] == url

