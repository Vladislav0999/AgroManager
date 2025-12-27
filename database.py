import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self):
        self.db_path = 'agrofarm.db'
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Створення таблиці полів
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            area REAL NOT NULL,
            soil_type TEXT,
            description TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Створення таблиці культур
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS crops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT CHECK(category IN ('grain', 'legume', 'oil')),
            sowing_season TEXT,
            harvest_period INTEGER,
            average_yield REAL,
            description TEXT
        )
        ''')
        
        # Створення таблиці плану посівів
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS planting_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id INTEGER,
            crop_id INTEGER,
            season_year TEXT,
            planned_area REAL,
            sowing_date DATE,
            expected_harvest_date DATE,
            status TEXT DEFAULT 'planned',
            FOREIGN KEY (field_id) REFERENCES fields (id),
            FOREIGN KEY (crop_id) REFERENCES crops (id)
        )
        ''')
        
        # Створення таблиці витрат
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id INTEGER,
            crop_id INTEGER,
            expense_type TEXT CHECK(expense_type IN ('seeds', 'fuel', 'fertilizers', 'chemicals', 'labor', 'equipment', 'other')),
            amount REAL NOT NULL,
            quantity REAL,
            unit TEXT,
            total_cost REAL,
            date DATE,
            description TEXT,
            FOREIGN KEY (field_id) REFERENCES fields (id),
            FOREIGN KEY (crop_id) REFERENCES crops (id)
        )
        ''')
        
        # Створення таблиці врожаю
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS harvest (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            field_id INTEGER,
            crop_id INTEGER,
            actual_yield REAL,
            harvest_date DATE,
            quality_rating INTEGER CHECK(quality_rating BETWEEN 1 AND 5),
            moisture_content REAL,
            notes TEXT,
            FOREIGN KEY (field_id) REFERENCES fields (id),
            FOREIGN KEY (crop_id) REFERENCES crops (id)
        )
        ''')
        
        # Додавання базових культур
        self.add_default_crops(cursor)
        
        conn.commit()
        conn.close()
    
    def add_default_crops(self, cursor):
        default_crops = [
            ('Пшениця озима', 'grain', 'осінь', 9, 4.5, 'Зернова культура'),
            ('Кукурудза', 'grain', 'весна', 5, 8.0, 'Зернова культура'),
            ('Ячмінь', 'grain', 'осінь', 9, 4.0, 'Зернова культура'),
            ('Соя', 'legume', 'весна', 4, 2.8, 'Бобова культура'),
            ('Соняшник', 'oil', 'весна', 4, 2.5, 'Олійна культура'),
            ('Ріпак', 'oil', 'осінь', 11, 3.0, 'Олійна культура'),
            ('Горох', 'legume', 'весна', 3, 2.2, 'Бобова культура'),
            ('Гречка', 'grain', 'весна', 3, 1.5, 'Крупяна культура')
        ]
        
        cursor.execute("SELECT COUNT(*) FROM crops")
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
            INSERT INTO crops (name, category, sowing_season, harvest_period, average_yield, description)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', default_crops)
    
    def execute_query(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()
        return cursor
    
    def fetch_all(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        return results
    
    def fetch_one(self, query, params=()):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        conn.close()
        return result

# Синглтон для доступу до бази даних
db = Database()