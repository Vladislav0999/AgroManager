from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QTextEdit, QHeaderView, QLabel, QSpinBox)
from PyQt6.QtCore import Qt
from database import db
from models import Crop

class CropDialog(QDialog):
    def __init__(self, crop=None, parent=None):
        super().__init__(parent)
        self.crop = crop
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Редагування культури" if self.crop else "Додати культуру")
        self.setFixedWidth(400)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        if self.crop:
            self.name_input.setText(self.crop.name)
        layout.addRow("Назва культури:", self.name_input)
        
        self.category_combo = QComboBox()
        self.category_combo.addItems(["grain", "legume", "oil"])
        if self.crop:
            index = self.category_combo.findText(self.crop.category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        layout.addRow("Категорія:", self.category_combo)
        
        self.season_combo = QComboBox()
        self.season_combo.addItems(["весна", "осінь", "літо", "зима"])
        if self.crop:
            index = self.season_combo.findText(self.crop.sowing_season)
            if index >= 0:
                self.season_combo.setCurrentIndex(index)
        layout.addRow("Сезон посіву:", self.season_combo)
        
        self.harvest_period_spin = QSpinBox()
        self.harvest_period_spin.setRange(1, 12)
        self.harvest_period_spin.setSuffix(" міс.")
        if self.crop:
            self.harvest_period_spin.setValue(self.crop.harvest_period)
        layout.addRow("Період збору:", self.harvest_period_spin)
        
        self.yield_input = QLineEdit()
        if self.crop:
            self.yield_input.setText(str(self.crop.average_yield))
        layout.addRow("Середня врожайність (т/га):", self.yield_input)
        
        self.description_input = QTextEdit()
        if self.crop:
            self.description_input.setText(self.crop.description)
        self.description_input.setMaximumHeight(80)
        layout.addRow("Опис:", self.description_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_crop)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def save_crop(self):
        name = self.name_input.text().strip()
        yield_text = self.yield_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Помилка", "Введіть назву культури")
            return
        
        try:
            avg_yield = float(yield_text)
            if avg_yield < 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Помилка", "Введіть коректну врожайність")
            return
        
        category_map = {"grain": "Зернові", "legume": "Бобові", "oil": "Олійні"}
        
        if self.crop:
            db.execute_query(
                """UPDATE crops SET name=?, category=?, sowing_season=?, 
                   harvest_period=?, average_yield=?, description=? WHERE id=?""",
                (name, self.category_combo.currentText(), 
                 self.season_combo.currentText(),
                 self.harvest_period_spin.value(),
                 avg_yield,
                 self.description_input.toPlainText(),
                 self.crop.id)
            )
        else:
            db.execute_query(
                """INSERT INTO crops (name, category, sowing_season, 
                   harvest_period, average_yield, description) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (name, self.category_combo.currentText(), 
                 self.season_combo.currentText(),
                 self.harvest_period_spin.value(),
                 avg_yield,
                 self.description_input.toPlainText())
            )
        
        self.accept()

class CropsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_crops()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Управління культурами")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Кнопки управління
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Додати культуру")
        self.add_btn.clicked.connect(self.add_crop)
        
        self.edit_btn = QPushButton("✏️ Редагувати")
        self.edit_btn.clicked.connect(self.edit_crop)
        
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.delete_btn.clicked.connect(self.delete_crop)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Всі", "Зернові", "Бобові", "Олійні"])
        self.filter_combo.currentTextChanged.connect(self.load_crops)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(QLabel("Фільтр:"))
        button_layout.addWidget(self.filter_combo)
        
        layout.addLayout(button_layout)
        
        # Таблиця культур
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Назва", "Категорія", "Сезон", "Період (міс)", "Урожайність", "Опис"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        self.setLayout(layout)
    
    def load_crops(self):
        filter_text = self.filter_combo.currentText()
        category_filter = {
            "Всі": "",
            "Зернові": "WHERE category='grain'",
            "Бобові": "WHERE category='legume'",
            "Олійні": "WHERE category='oil'"
        }
        
        where_clause = category_filter[filter_text]
        query = f"SELECT * FROM crops {where_clause} ORDER BY name"
        
        crops = db.fetch_all(query)
        self.table.setRowCount(len(crops))
        
        category_names = {"grain": "Зернові", "legume": "Бобові", "oil": "Олійні"}
        
        for row_idx, crop in enumerate(crops):
            category_name = category_names.get(crop[2], crop[2])
            
            for col_idx in range(7):
                if col_idx == 2:  # Категорія
                    value = category_name
                elif col_idx == 6:  # Опис
                    value = crop[6] if crop[6] else ""
                else:
                    value = str(crop[col_idx]) if crop[col_idx] else ""
                
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
    
    def add_crop(self):
        dialog = CropDialog()
        if dialog.exec():
            self.load_crops()
    
    def edit_crop(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть культуру для редагування")
            return
        
        row = selected[0].row()
        crop_id = int(self.table.item(row, 0).text())
        
        crop_data = db.fetch_one("SELECT * FROM crops WHERE id = ?", (crop_id,))
        if crop_data:
            crop = Crop(
                id=crop_data[0],
                name=crop_data[1],
                category=crop_data[2],
                sowing_season=crop_data[3],
                harvest_period=crop_data[4],
                average_yield=crop_data[5],
                description=crop_data[6]
            )
            
            dialog = CropDialog(crop, self)
            if dialog.exec():
                self.load_crops()
    
    def delete_crop(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть культуру для видалення")
            return
        
        reply = QMessageBox.question(
            self, "Підтвердження",
            "Видалити обрану культуру?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            crop_id = int(self.table.item(row, 0).text())
            db.execute_query("DELETE FROM crops WHERE id = ?", (crop_id,))
            self.load_crops()