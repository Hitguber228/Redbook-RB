import sqlite3
import json
import os
from typing import List, Optional, Dict, Any
from .seed_data import INITIAL_SPECIES_DATA, INITIAL_QUIZZES_DATA

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "redbook.db"))

class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_tables()
        self._seed_initial_data()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Таблица видов Красной книги РБ
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS species (
                id TEXT PRIMARY KEY,
                name_ru TEXT NOT NULL,
                name_be TEXT NOT NULL,
                name_lat TEXT NOT NULL,
                kingdom TEXT NOT NULL,
                taxon_group TEXT NOT NULL,
                category TEXT NOT NULL,
                description_ru TEXT NOT NULL,
                description_be TEXT NOT NULL,
                morphology TEXT NOT NULL,
                look_alike_species TEXT,
                habitat TEXT NOT NULL,
                distribution_rb TEXT NOT NULL, -- JSON list
                national_parks TEXT NOT NULL,   -- JSON list
                limiting_factors TEXT NOT NULL,
                protection_measures TEXT NOT NULL,
                phenology_months TEXT NOT NULL,  -- JSON list of ints
                image_url TEXT NOT NULL,
                sound_url TEXT,
                sound_title TEXT,
                coordinates_json TEXT,          -- JSON list of [lat, lng]
                is_featured INTEGER DEFAULT 0,
                biotope TEXT DEFAULT 'forest'
            )
            """)

            # Таблица образовательных викторин
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY,
                quiz_type TEXT NOT NULL,
                question_ru TEXT NOT NULL,
                question_be TEXT NOT NULL,
                options_ru TEXT NOT NULL, -- JSON list
                options_be TEXT NOT NULL, -- JSON list
                correct_index INTEGER NOT NULL,
                explanation_ru TEXT NOT NULL,
                explanation_be TEXT NOT NULL,
                media_url TEXT,
                related_species_id TEXT
            )
            """)

            # Таблица полевых наблюдений (Citizen Science)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                species_id TEXT,
                species_guess TEXT NOT NULL,
                user_name TEXT NOT NULL,
                notes TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                date_created TEXT NOT NULL,
                photo_path TEXT
            )
            """)

            # Таблица избранных видов (Закладки)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookmarks (
                species_id TEXT PRIMARY KEY
            )
            """)

            conn.commit()

    def _seed_initial_data(self):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM species")
            species_count = cursor.fetchone()[0]
            if species_count < len(INITIAL_SPECIES_DATA):
                for s in INITIAL_SPECIES_DATA:
                    cursor.execute("""
                    INSERT OR REPLACE INTO species (
                        id, name_ru, name_be, name_lat, kingdom, taxon_group, category,
                        description_ru, description_be, morphology, look_alike_species,
                        habitat, distribution_rb, national_parks, limiting_factors,
                        protection_measures, phenology_months, image_url, sound_url,
                        sound_title, coordinates_json, is_featured, biotope
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        s["id"],
                        s["name_ru"],
                        s["name_be"],
                        s["name_lat"],
                        s["kingdom"],
                        s["taxon_group"],
                        s["category"],
                        s["description_ru"],
                        s["description_be"],
                        s["morphology"],
                        s.get("look_alike_species"),
                        s["habitat"],
                        json.dumps(s["distribution_rb"], ensure_ascii=False),
                        json.dumps(s["national_parks"], ensure_ascii=False),
                        s["limiting_factors"],
                        s["protection_measures"],
                        json.dumps(s["phenology_months"]),
                        s["image_url"],
                        s.get("sound_url"),
                        s.get("sound_title"),
                        json.dumps(s.get("coordinates", [])),
                        1 if s.get("is_featured") else 0,
                        s.get("biotope", "forest")
                    ))

            cursor.execute("SELECT COUNT(*) FROM quizzes")
            quizzes_count = cursor.fetchone()[0]
            if quizzes_count < len(INITIAL_QUIZZES_DATA):
                for q in INITIAL_QUIZZES_DATA:
                    cursor.execute("""
                    INSERT OR REPLACE INTO quizzes (
                        id, quiz_type, question_ru, question_be, options_ru, options_be,
                        correct_index, explanation_ru, explanation_be, media_url, related_species_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            q["id"],
                            q["quiz_type"],
                            q["question_ru"],
                            q["question_be"],
                            json.dumps(q["options_ru"], ensure_ascii=False),
                            json.dumps(q["options_be"], ensure_ascii=False),
                            q["correct_index"],
                            q["explanation_ru"],
                            q["explanation_be"],
                            q.get("media_url"),
                            q.get("related_species_id")
                        ))

            conn.commit()

    def get_species(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        kingdom: Optional[str] = None,
        region: Optional[str] = None,
        taxon_group: Optional[str] = None,
        national_park: Optional[str] = None,
        biotope: Optional[str] = None,
        sort_by: str = "name_asc",
        language: str = "ru",
        has_sound_only: bool = False,
        featured_only: bool = False
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            sql = "SELECT * FROM species WHERE 1=1"
            params = []

            if featured_only:
                sql += " AND is_featured = 1"
            if has_sound_only:
                sql += " AND sound_url IS NOT NULL AND sound_url != ''"
            if category:
                sql += " AND category = ?"
                params.append(category)
            if kingdom:
                sql += " AND kingdom = ?"
                params.append(kingdom)
            if taxon_group:
                sql += " AND taxon_group = ?"
                params.append(taxon_group)
            if biotope:
                sql += " AND biotope = ?"
                params.append(biotope)
            if national_park:
                sql += " AND national_parks LIKE ?"
                params.append(f"%{national_park}%")
            if region:
                # Нормализация для поиска в JSON
                reg_clean = region.replace(" вобласць", "").replace(" область", "").strip()
                # Соответствия белорусских и русских названий областей
                reg_map = {
                    "Брэсцкая": "Брест",
                    "Брестская": "Брест",
                    "Віцебская": "Витеб",
                    "Витебская": "Витеб",
                    "Гомельская": "Гомел",
                    "Гродзенская": "Гродн",
                    "Гродненская": "Гродн",
                    "Мінская": "Минск",
                    "Минская": "Минск",
                    "Магілёўская": "Могилев",
                    "Могилевская": "Могилев"
                }
                reg_root = reg_map.get(reg_clean, reg_clean[:4])
                sql += " AND distribution_rb LIKE ?"
                params.append(f"%{reg_root}%")
            if query:
                q = f"%{query.strip().lower()}%"
                sql += " AND (LOWER(name_ru) LIKE ? OR LOWER(name_be) LIKE ? OR LOWER(name_lat) LIKE ? OR LOWER(habitat) LIKE ?)"
                params.extend([q, q, q, q])

            # Сортировка на уровне SQL
            name_col = "name_be" if language == "be" else "name_ru"
            if sort_by == "name_asc":
                sql += f" ORDER BY {name_col} ASC"
            elif sort_by == "name_desc":
                sql += f" ORDER BY {name_col} DESC"
            elif sort_by == "category_asc":
                sql += f" ORDER BY category ASC, {name_col} ASC"
            elif sort_by == "category_desc":
                sql += f" ORDER BY category DESC, {name_col} ASC"

            cursor.execute(sql, params)
            rows = cursor.fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["distribution_rb"] = json.loads(item["distribution_rb"])
                item["national_parks"] = json.loads(item["national_parks"])
                item["phenology_months"] = json.loads(item["phenology_months"])
                item["coordinates"] = json.loads(item["coordinates_json"] or "[]")
                item["is_featured"] = bool(item["is_featured"])
                result.append(item)

            if sort_by == "regions_desc":
                result.sort(key=lambda s: len(s.get("distribution_rb", [])), reverse=True)

            return result

    def get_species_by_id(self, species_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM species WHERE id = ?", (species_id,))
            row = cursor.fetchone()
            if not row:
                return None
            item = dict(row)
            item["distribution_rb"] = json.loads(item["distribution_rb"])
            item["national_parks"] = json.loads(item["national_parks"])
            item["phenology_months"] = json.loads(item["phenology_months"])
            item["coordinates"] = json.loads(item["coordinates_json"] or "[]")
            item["is_featured"] = bool(item["is_featured"])
            return item

    def get_quizzes(self, quiz_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if quiz_type:
                cursor.execute("SELECT * FROM quizzes WHERE quiz_type = ?", (quiz_type,))
            else:
                cursor.execute("SELECT * FROM quizzes")
            rows = cursor.fetchall()
            result = []
            for row in rows:
                item = dict(row)
                item["options_ru"] = json.loads(item["options_ru"])
                item["options_be"] = json.loads(item["options_be"])
                result.append(item)
            return result

    def add_observation(self, species_guess: str, user_name: str, notes: str, lat: float, lng: float, date_str: str, photo_path: Optional[str] = None, species_id: Optional[str] = None) -> int:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO observations (species_id, species_guess, user_name, notes, latitude, longitude, date_created, photo_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (species_id, species_guess, user_name, notes, lat, lng, date_str, photo_path))
            conn.commit()
            return cursor.lastrowid

    def get_observations(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM observations ORDER BY id DESC")
            return [dict(r) for r in cursor.fetchall()]

db_manager = DatabaseManager()

