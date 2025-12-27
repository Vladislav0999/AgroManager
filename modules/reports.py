from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from database import db

class ReportsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Звіти")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        self.report_combo = QComboBox()
        self.report_combo.addItems([
            "Поля",
            "Культури",
            "Витрати",
            "Урожай"
        ])
        self.report_combo.currentTextChanged.connect(self.show_report)
        layout.addWidget(self.report_combo)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        self.setLayout(layout)
        
        self.show_report()
    
    def show_report(self):
        report_type = self.report_combo.currentText()
        
        if report_type == "Поля":
            self.show_fields()
        elif report_type == "Культури":
            self.show_crops()
        elif report_type == "Витрати":
            self.show_expenses()
        elif report_type == "Урожай":
            self.show_harvest()
    
    def show_fields(self):
        fields = db.fetch_all("SELECT * FROM fields ORDER BY name")
        text = "ЗВІТ ПО ПОЛЯХ\n"
        text += "=" * 40 + "\n\n"
        
        total_area = 0
        for field in fields:
            text += f"Поле: {field[1]}\n"
            text += f"Площа: {field[2]} га\n"
            text += f"Тип ґрунту: {field[3]}\n"
            text += f"Опис: {field[4]}\n"
            text += "-" * 40 + "\n"
            total_area += field[2]
        
        text += f"\nЗагальна площа: {total_area} га\n"
        text += f"Кількість полів: {len(fields)}"
        
        self.text_edit.setText(text)
    
    def show_crops(self):
        crops = db.fetch_all("SELECT * FROM crops ORDER BY name")
        text = "ЗВІТ ПО КУЛЬТУРАХ\n"
        text += "=" * 40 + "\n\n"
        
        categories = {"grain": 0, "legume": 0, "oil": 0}
        for crop in crops:
            cat = crop[2]
            if cat in categories:
                categories[cat] += 1
            
            text += f"Культура: {crop[1]}\n"
            text += f"Категорія: {cat}\n"
            text += f"Сезон: {crop[3]}\n"
            text += f"Урожайність: {crop[5]} т/га\n"
            text += "-" * 40 + "\n"
        
        text += f"\nСтатистика:\n"
        text += f"Зернові: {categories['grain']}\n"
        text += f"Бобові: {categories['legume']}\n"
        text += f"Олійні: {categories['oil']}\n"
        text += f"Всього: {len(crops)}"
        
        self.text_edit.setText(text)
    
    def show_expenses(self):
        expenses = db.fetch_all("SELECT * FROM expenses ORDER BY date DESC")
        text = "ЗВІТ ПО ВИТРАТАХ\n"
        text += "=" * 40 + "\n\n"
        
        total = 0
        for exp in expenses:
            text += f"Тип: {exp[3]}\n"
            text += f"Сума: {exp[4]} грн\n"
            text += f"Дата: {exp[5]}\n"
            text += f"Опис: {exp[6]}\n"
            text += "-" * 40 + "\n"
            total += exp[4]
        
        text += f"\nЗагальна сума: {total} грн\n"
        text += f"Кількість записів: {len(expenses)}"
        
        self.text_edit.setText(text)
    
    def show_harvest(self):
        harvest = db.fetch_all("SELECT * FROM harvest ORDER BY harvest_date DESC")
        text = "ЗВІТ ПО УРОЖАЮ\n"
        text += "=" * 40 + "\n\n"
        
        total_yield = 0
        for h in harvest:
            text += f"Урожай: {h[3]} т\n"
            text += f"Дата: {h[4]}\n"
            text += f"Якість: {h[5]}/5\n"
            text += "-" * 40 + "\n"
            total_yield += h[3]
        
        text += f"\nЗагальний урожай: {total_yield} т\n"
        text += f"Кількість записів: {len(harvest)}"
        
        self.text_edit.setText(text)