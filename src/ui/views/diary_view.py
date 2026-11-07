import flet as ft
import os
import csv
from datetime import datetime
from typing import Callable
from ...database.db import db_manager
from ..theme import AppColors

class DiaryView(ft.Container):
    def __init__(self, get_language: Callable[[], str]):
        super().__init__()
        self.expand = True
        self.get_language = get_language
        self._build_ui()

    def _build_ui(self):
        lang = self.get_language()
        observations = db_manager.get_observations()

        self.name_field = ft.TextField(
            label="Ваше имя / Учащийся-исследователь" if lang == "ru" else "Ваша імя / Навучэнец-даследчык",
            value="Юный натуралист",
            border_radius=10,
            filled=True
        )

        self.species_field = ft.TextField(
            label="Предполагаемый вид" if lang == "ru" else "Меркаваны від",
            hint_text="Например: Европейская рысь, Зубр, Болотная черепаха...",
            border_radius=10,
            filled=True
        )

        self.notes_field = ft.TextField(
            label="Заметки о биотопе и поведении" if lang == "ru" else "Нататкі аб біятопе і паводзінах",
            hint_text="Опишите характер леса/болота, поведение особи, следы жизнедеятельности...",
            multiline=True,
            min_lines=2,
            border_radius=10,
            filled=True
        )

        obs_cards = []
        if not observations:
            obs_cards.append(
                ft.Container(
                    padding=30,
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.AUTO_STORIES, size=48, color=ft.Colors.GREY_400),
                            ft.Text(
                                "Пока нет сохраненных наблюдений" if lang == "ru" else "Пакуль няма захаваных назіранняў",
                                weight=ft.FontWeight.BOLD,
                                size=15
                            ),
                            ft.Text(
                                "Заполните форму выше, чтобы зафиксировать встречу краснокнижника в дикой природе Беларуси!" if lang == "ru" else "Запоўніце форму вышэй, каб зафіксаваць сустрэчу рэдкага віду!",
                                size=12,
                                color=ft.Colors.GREY_600,
                                text_align=ft.TextAlign.CENTER
                            )
                        ]
                    )
                )
            )
        else:
            for obs in observations:
                obs_cards.append(
                    ft.Card(
                        elevation=1,
                        content=ft.Container(
                            padding=14,
                            content=ft.Column(
                                spacing=6,
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(obs["species_guess"], size=16, weight=ft.FontWeight.BOLD),
                                            ft.Row(
                                                tight=True,
                                                spacing=4,
                                                controls=[
                                                    ft.Icon(ft.Icons.CALENDAR_TODAY, size=12, color=AppColors.TEXT_MUTED_LIGHT),
                                                    ft.Text(obs['date_created'], size=11, color=AppColors.TEXT_MUTED_LIGHT)
                                                ]
                                            )
                                        ]
                                    ),
                                    ft.Text(f"Наблюдатель: {obs['user_name']}", size=12, color=AppColors.PRIMARY, weight=ft.FontWeight.W_600),
                                    ft.Text(obs["notes"], size=13),
                                    ft.Row(
                                        tight=True,
                                        spacing=4,
                                        controls=[
                                            ft.Icon(ft.Icons.MY_LOCATION, size=12, color=ft.Colors.GREY_600),
                                            ft.Text(f"GPS фиксация: {obs['latitude']:.4f}, {obs['longitude']:.4f}", size=11, color=ft.Colors.GREY_600)
                                        ]
                                    )
                                ]
                            )
                        )
                    )
                )

        self.export_status = ft.Text("", size=12, color=ft.Colors.GREEN_700, weight=ft.FontWeight.BOLD)

        self.content = ft.ListView(
            expand=True,
            padding=ft.Padding.symmetric(horizontal=16, vertical=16),
            spacing=16,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Полевой дневник натуралиста (Citizen Science)" if lang == "ru" else "Палявы дзённік натураліста (Citizen Science)",
                            size=22,
                            weight=ft.FontWeight.BOLD
                        ),
                        ft.Text(
                            "Фиксация находок редких видов в дикой природе Беларуси. Работает 100% автономно в полевых условиях без интернета!" if lang == "ru" else "Фіксацыя знаходак рэдкіх відаў у дзікай прыродзе Беларусі. Працуе 100% аўтаномна ў палявых умовах без інтэрнэту!",
                            size=13,
                            color=AppColors.TEXT_MUTED_LIGHT
                        )
                    ]
                ),
                # Карточка добавления наблюдения
                ft.Card(
                    elevation=2,
                    content=ft.Container(
                        padding=18,
                        content=ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    spacing=8,
                                    controls=[
                                        ft.Icon(ft.Icons.NOTE_ADD, color=AppColors.PRIMARY, size=22),
                                        ft.Text("Новая полевая запись" if lang == "ru" else "Новы палявы запіс", size=16, weight=ft.FontWeight.BOLD)
                                    ]
                                ),
                                self.name_field,
                                self.species_field,
                                self.notes_field,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.END,
                                    controls=[
                                        ft.FilledButton(
                                            content="Зафиксировать в дневнике" if lang == "ru" else "Зафіксаваць у дзённіку",
                                            icon=ft.Icons.SAVE,
                                            on_click=self._save_observation
                                        )
                                    ]
                                )
                            ]
                        )
                    )
                ),
                ft.Divider(height=1),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("История полевых находок:" if lang == "ru" else "Гісторыя палявых знаходак:", weight=ft.FontWeight.BOLD, size=15),
                        ft.FilledButton(
                            content="Экспорт в CSV для отчета" if lang == "ru" else "Экспарт у CSV для справаздачы",
                            icon=ft.Icons.DOWNLOAD,
                            style=ft.ButtonStyle(bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, color=ft.Colors.ON_SURFACE),
                            on_click=self._export_to_csv
                        )
                    ]
                ),
                self.export_status,
                ft.Column(spacing=10, controls=obs_cards),
                ft.Container(height=24) # Bottom padding
            ]
        )

    def _save_observation(self, e):
        guess = self.species_field.value
        if not guess:
            return
        user = self.name_field.value or "Натуралист"
        notes = self.notes_field.value or "Встречен в естественной среде обитания."
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        db_manager.add_observation(
            species_guess=guess,
            user_name=user,
            notes=notes,
            lat=53.9000,
            lng=27.5600,
            date_str=now_str
        )

        self.species_field.value = ""
        self.notes_field.value = ""
        self._build_ui()
        self.update()

    def _export_to_csv(self, e):
        observations = db_manager.get_observations()
        if not observations:
            self.export_status.value = "Нет наблюдений для экспорта!"
            self.export_status.color = ft.Colors.AMBER_800
            self.export_status.update()
            return

        export_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "field_observations_report.csv"))
        
        with open(export_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["ID", "Наблюдатель", "Предполагаемый вид", "Заметки о биотопе", "Широта (GPS)", "Долгота (GPS)", "Дата и время фиксации"])
            for o in observations:
                writer.writerow([
                    o["id"],
                    o["user_name"],
                    o["species_guess"],
                    o["notes"],
                    f"{o['latitude']:.4f}",
                    f"{o['longitude']:.4f}",
                    o["date_created"]
                ])

        self.export_status.value = f"Отчет успешно экспортирован в {os.path.basename(export_path)} ({len(observations)} записей)!"
        self.export_status.color = ft.Colors.GREEN_700
        self.export_status.update()
