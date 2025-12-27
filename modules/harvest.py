from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QTextEdit, QHeaderView, QLabel, QDateEdit, 
                             QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt, QDate
from database import db
from models import Harvest

class HarvestDialog(QDialog):
    def __init__(self, harvest=None, parent=None):
        super().__init__(parent)
        self.harvest = harvest
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Редагування врожаю" if self.harvest else "Додати врожай")
        self.setFixedWidth(400)
        
        layout = QFormLayout()
        
        # Отримання списків полів і культур
        fields = db.fetch_all("SELECT id, name FROM fields")
        crops = db.fetch_all("SELECT id, name FROM crops")
        
        self.field_combo = QComboBox()
        for field in fields:
            self.field_combo.addItem(f"{field[0]}. {field[1]}", field[0])
        
        if self.harvest:
            index = self.field_combo.findData(self.harvest.field_id)
            if index >= 0:
                self.field_combo.setCurrentIndex(index)
        
        layout.addRow("Поле:", self.field_combo)
        
        self.crop_combo = QComboBox()
        for crop in crops:
            self.crop_combo.addItem(f"{crop[0]}. {crop[1]}", crop[0])
        
        if self.harvest:
            index = self.crop_combo.findData(self.harvest.crop_id)
            if index >= 0:
                self.crop_combo.setCurrentIndex(index)
        
        layout.addRow("Культура:", self.crop_combo)
        
        self.yield_input = QDoubleSpinBox()
        self.yield_input.setRange(0, 1000)
        self.yield_input.setSuffix(" т")
        self.yield_input.setDecimals(2)
        if self.harvest:
            self.yield_input.setValue(self.harvest.actual_yield)
        layout.addRow("Фактичний врожай:", self.yield_input)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        if self.harvest and self.harvest.harvest_date:
            self.date_edit.setDate(QDate.fromString(self.harvest.harvest_date, "yyyy-MM-dd"))
        layout.addRow("Дата збору:", self.date_edit)
        
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 5)
        self.quality_spin.setPrefix("★ ")
        if self.harvest:
            self.quality_spin.setValue(self.harvest.quality_rating)
        layout.addRow("Якість (1-5):", self.quality_spin)
        
        self.moisture_input = QDoubleSpinBox()
        self.moisture_input.setRange(0, 100)
        self.moisture_input.setSuffix(" %")
        self.moisture_input.setDecimals(1)
        if self.harvest:
            self.moisture_input.setValue(self.harvest.moisture_content)
        layout.addRow("Вологість:", self.moisture_input)
        
        self.notes_input = QTextEdit()
        if self.harvest:
            self.notes_input.setText(self.harvest.notes)
        self.notes_input.setMaximumHeight(80)
        layout.addRow("Примітки:", self.notes_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_harvest)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def save_harvest(self):
        if self.harvest:
            db.execute_query(
                """UPDATE harvest SET field_id=?, crop_id=?, actual_yield=?, 
                   harvest_date=?, quality_rating=?, moisture_content=?, notes=? 
                   WHERE id=?""",
                (self.field_combo.currentData(),
                 self.crop_combo.currentData(),
                 self.yield_input.value(),
                 self.date_edit.date().toString("yyyy-MM-dd"),
                 self.quality_spin.value(),
                 self.moisture_input.value(),
                 self.notes_input.toPlainText(),
                 self.harvest.id)
            )
        else:
            db.execute_query(
                """INSERT INTO harvest 
                   (field_id, crop_id, actual_yield, harvest_date, 
                    quality_rating, moisture_content, notes) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (self.field_combo.currentData(),
                 self.crop_combo.currentData(),
                 self.yield_input.value(),
                 self.date_edit.date().toString("yyyy-MM-dd"),
                 self.quality_spin.value(),
                 self.moisture_input.value(),
                 self.notes_input.toPlainText())
            )
        
        self.accept()

class HarvestModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_harvests()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Облік урожайності")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Фільтри
        filter_layout = QHBoxLayout()
        
        self.year_combo = QComboBox()
        self.year_combo.addItems(["Всі роки", "2024", "2023", "2022"])
        self.year_combo.currentTextChanged.connect(self.load_harvests)
        
        filter_layout.addWidget(QLabel("Рік:"))
        filter_layout.addWidget(self.year_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Кнопки управління
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Додати врожай")
        self.add_btn.clicked.connect(self.add_harvest)
        
        self.edit_btn = QPushButton("✏️ Редагувати")
        self.edit_btn.clicked.connect(self.edit_harvest)
        
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.delete_btn.clicked.connect(self.delete_harvest)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Таблиця врожаю
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Поле", "Культура", "Урожай (т)", "Дата", "Якість", "Вологість", "Примітки"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; padding: 5px; font-weight: bold;")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def load_harvests(self):
        year = self.year_combo.currentText()
        
        query = """SELECT h.id, f.name, c.name, h.actual_yield, 
                   h.harvest_date, h.quality_rating, 
                   h.moisture_content, h.notes 
                   FROM harvest h
                   LEFT JOIN fields f ON h.field_id = f.id
                   LEFT JOIN crops c ON h.crop_id = c.id
                   WHERE 1=1"""
        
        params = []
        
        if year != "Всі роки":
            query += " AND strftime('%Y', h.harvest_date) = ?"
            params.append(year)
        
        query += " ORDER BY h.harvest_date DESC"
        
        harvests = db.fetch_all(query, tuple(params))
        self.table.setRowCount(len(harvests))
        
        total_yield = 0
        avg_quality = 0
        
        for row_idx, harvest in enumerate(harvests):
            total_yield += harvest[3] if harvest[3] else 0
            avg_quality += harvest[5] if harvest[5] else 0
            
            for col_idx in range(8):
                if col_idx == 0:  # ID
                    value = str(harvest[0])
                elif col_idx == 3:  # Урожай
                    value = f"{harvest[3]:.2f} т" if harvest[3] else "0.00 т"
                elif col_idx == 4:  # Дата
                    value = harvest[4] if harvest[4] else ""
                elif col_idx == 5:  # Якість
                    stars = "★" * (harvest[5] if harvest[5] else 0)
                    value = f"{stars} ({harvest[5]})" if harvest[5] else ""
                elif col_idx == 6:  # Вологість
                    value = f"{harvest[6]:.1f}%" if harvest[6] else ""
                elif col_idx == 7:  # Примітки
                    value = harvest[7] if harvest[7] else ""
                else:  # Назви полів та культур
                    value = harvest[col_idx] if harvest[col_idx] else "--"
                
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        if len(harvests) > 0:
            avg_quality = avg_quality / len(harvests)
        
        self.stats_label.setText(f"Загальний врожай: {total_yield:.2f} т | Середня якість: {avg_quality:.1f}/5 | Записів: {len(harvests)}")
    
    def add_harvest(self):
        dialog = HarvestDialog()
        if dialog.exec():
            self.load_harvests()
    
    def edit_harvest(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для редагування")
            return
        
        row = selected[0].row()
        harvest_id = int(self.table.item(row, 0).text())
        
        harvest_data = db.fetch_one("SELECT * FROM harvest WHERE id = ?", (harvest_id,))
        if harvest_data:
            harvest = Harvest(
                id=harvest_data[0],
                field_id=harvest_data[1],
                crop_id=harvest_data[2],
                actual_yield=harvest_data[3],
                harvest_date=harvest_data[4],
                quality_rating=harvest_data[5],
                moisture_content=harvest_data[6],
                notes=harvest_data[7]
            )
            
            dialog = HarvestDialog(harvest, self)
            if dialog.exec():
                self.load_harvests()
    
    def delete_harvest(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення")
            return
        
        reply = QMessageBox.question(
            self, "Підтвердження",
            "Видалити обраний запис врожаю?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            harvest_id = int(self.table.item(row, 0).text())
            db.execute_query("DELETE FROM harvest WHERE id = ?", (harvest_id,))
            self.load_harvests()