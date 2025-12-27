from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# Імпорт модулів
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.fields import FieldsModule
from modules.crops import CropsModule
from modules.expenses import ExpensesModule
from modules.harvest import HarvestModule
from modules.reports import ReportsModule
from database import db

class AddPlantingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Додати план посіву")
        self.setFixedWidth(400)
        
        layout = QFormLayout()
        
        # Отримання списків полів і культур
        fields = db.fetch_all("SELECT id, name FROM fields ORDER BY name")
        crops = db.fetch_all("SELECT id, name FROM crops ORDER BY name")
        
        self.field_combo = QComboBox()
        for field in fields:
            self.field_combo.addItem(field[1], field[0])
        layout.addRow("Поле:", self.field_combo)
        
        self.crop_combo = QComboBox()
        for crop in crops:
            self.crop_combo.addItem(crop[1], crop[0])
        layout.addRow("Культура:", self.crop_combo)
        
        self.season_combo = QComboBox()
        self.season_combo.addItems(["2024-2025", "2023-2024", "2022-2023"])
        layout.addRow("Сезон/Рік:", self.season_combo)
        
        self.area_input = QLineEdit()
        layout.addRow("Площа (га):", self.area_input)
        
        self.sowing_date = QDateEdit()
        self.sowing_date.setCalendarPopup(True)
        self.sowing_date.setDate(QDate.currentDate())
        layout.addRow("Дата посіву:", self.sowing_date)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["planned", "in_progress", "completed", "cancelled"])
        layout.addRow("Статус:", self.status_combo)
        
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_planning)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def save_planning(self):
        try:
            area = float(self.area_input.text())
            
            db.execute_query(
                """INSERT INTO planting_plans 
                   (field_id, crop_id, season_year, planned_area, 
                    sowing_date, status) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (self.field_combo.currentData(),
                 self.crop_combo.currentData(),
                 self.season_combo.currentText(),
                 area,
                 self.sowing_date.date().toString("yyyy-MM-dd"),
                 self.status_combo.currentText())
            )
            
            self.accept()
        except ValueError:
            QMessageBox.warning(self, "Помилка", "Введіть коректну площу")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AgroFarm Manager")
        self.setGeometry(100, 100, 1200, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        title_label = QLabel("🌾 AgroFarm Manager")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        nav_layout = QHBoxLayout()
        
        self.fields_btn = QPushButton("📌 Поля")
        self.crops_btn = QPushButton("🌱 Культури")
        self.expenses_btn = QPushButton("💰 Витрати")
        self.harvest_btn = QPushButton("📊 Урожайність")
        self.reports_btn = QPushButton("📈 Звіти")
        self.planning_btn = QPushButton("📅 Планування")
        
        for btn in [self.fields_btn, self.crops_btn, self.expenses_btn, 
                   self.harvest_btn, self.reports_btn, self.planning_btn]:
            btn.setMinimumHeight(40)
        
        nav_layout.addWidget(self.fields_btn)
        nav_layout.addWidget(self.crops_btn)
        nav_layout.addWidget(self.expenses_btn)
        nav_layout.addWidget(self.harvest_btn)
        nav_layout.addWidget(self.reports_btn)
        nav_layout.addWidget(self.planning_btn)
        
        main_layout.addLayout(nav_layout)
        
        self.stacked_widget = QStackedWidget()
        
        self.fields_module = FieldsModule()
        self.crops_module = CropsModule()
        self.expenses_module = ExpensesModule()
        self.harvest_module = HarvestModule()
        self.reports_module = ReportsModule()
        
        self.stacked_widget.addWidget(self.fields_module)
        self.stacked_widget.addWidget(self.crops_module)
        self.stacked_widget.addWidget(self.expenses_module)
        self.stacked_widget.addWidget(self.harvest_module)
        self.stacked_widget.addWidget(self.reports_module)
        
        main_layout.addWidget(self.stacked_widget)
        
        self.fields_btn.clicked.connect(lambda: self.switch_module(0))
        self.crops_btn.clicked.connect(lambda: self.switch_module(1))
        self.expenses_btn.clicked.connect(lambda: self.switch_module(2))
        self.harvest_btn.clicked.connect(lambda: self.switch_module(3))
        self.reports_btn.clicked.connect(lambda: self.switch_module(4))
        self.planning_btn.clicked.connect(self.show_planning_dialog)
        
        central_widget.setLayout(main_layout)
        
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готово")
        
        self.create_menu()
        self.switch_module(0)
    
    def create_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("Файл")
        exit_action = QAction("Вихід", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
    
    def switch_module(self, index):
        self.stacked_widget.setCurrentIndex(index)
        modules = ["Поля", "Культури", "Витрати", "Урожайність", "Звіти"]
        self.status_bar.showMessage(f"Модуль: {modules[index]}")
    
    def show_planning_dialog(self):
        dialog = AddPlantingDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "Успіх", "План посіву додано")