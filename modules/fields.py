from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QTextEdit, QHeaderView, QLabel)
from PyQt6.QtCore import Qt
from database import db
from models import Field

class FieldDialog(QDialog):
    def __init__(self, field=None, parent=None):
        super().__init__(parent)
        self.field = field
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Редагування поля" if self.field else "Додати поле")
        self.setFixedWidth(400)
        
        layout = QFormLayout()
        
        self.name_input = QLineEdit()
        if self.field:
            self.name_input.setText(self.field.name)
        layout.addRow("Назва поля:", self.name_input)
        
        self.area_input = QLineEdit()
        if self.field:
            self.area_input.setText(str(self.field.area))
        layout.addRow("Площа (га):", self.area_input)
        
        self.soil_type_combo = QComboBox()
        self.soil_type_combo.addItems(["Чорнозем", "Супісок", "Глинистий", "Торф'янистий", "Піщаний"])
        if self.field:
            index = self.soil_type_combo.findText(self.field.soil_type)
            if index >= 0:
                self.soil_type_combo.setCurrentIndex(index)
        layout.addRow("Тип ґрунту:", self.soil_type_combo)
        
        self.description_input = QTextEdit()
        if self.field:
            self.description_input.setText(self.field.description)
        self.description_input.setMaximumHeight(100)
        layout.addRow("Опис:", self.description_input)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_field)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def save_field(self):
        name = self.name_input.text().strip()
        area_text = self.area_input.text().strip()
        
        if not name:
            QMessageBox.warning(self, "Помилка", "Введіть назву поля")
            return
        
        try:
            area = float(area_text)
            if area <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Помилка", "Введіть коректну площу")
            return
        
        if self.field:
            # Оновлення
            db.execute_query(
                "UPDATE fields SET name=?, area=?, soil_type=?, description=? WHERE id=?",
                (name, area, self.soil_type_combo.currentText(), 
                 self.description_input.toPlainText(), self.field.id)
            )
        else:
            # Додавання
            db.execute_query(
                "INSERT INTO fields (name, area, soil_type, description) VALUES (?, ?, ?, ?)",
                (name, area, self.soil_type_combo.currentText(), 
                 self.description_input.toPlainText())
            )
        
        self.accept()

class FieldsModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_fields()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Управління полями")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Кнопки управління
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Додати поле")
        self.add_btn.clicked.connect(self.add_field)
        
        self.edit_btn = QPushButton("✏️ Редагувати")
        self.edit_btn.clicked.connect(self.edit_field)
        
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.delete_btn.clicked.connect(self.delete_field)
        
        self.refresh_btn = QPushButton("🔄 Оновити")
        self.refresh_btn.clicked.connect(self.load_fields)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(button_layout)
        
        # Таблиця полів
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Назва", "Площа (га)", "Тип ґрунту", "Дата створення"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def load_fields(self):
        fields = db.fetch_all("SELECT * FROM fields ORDER BY id")
        self.table.setRowCount(len(fields))
        
        total_area = 0
        for row_idx, field in enumerate(fields):
            total_area += field[2]
            for col_idx in range(5):
                item = QTableWidgetItem(str(field[col_idx]) if field[col_idx] else "")
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        self.stats_label.setText(f"Загальна площа: {total_area:.2f} га | Кількість полів: {len(fields)}")
    
    def add_field(self):
        dialog = FieldDialog()
        if dialog.exec():
            self.load_fields()
    
    def edit_field(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть поле для редагування")
            return
        
        row = selected[0].row()
        field_id = int(self.table.item(row, 0).text())
        
        field_data = db.fetch_one("SELECT * FROM fields WHERE id = ?", (field_id,))
        if field_data:
            field = Field(
                id=field_data[0],
                name=field_data[1],
                area=field_data[2],
                soil_type=field_data[3],
                description=field_data[4],
                created_date=field_data[5]
            )
            
            dialog = FieldDialog(field, self)
            if dialog.exec():
                self.load_fields()
    
    def delete_field(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть поле для видалення")
            return
        
        reply = QMessageBox.question(
            self, "Підтвердження",
            "Видалити обране поле?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            field_id = int(self.table.item(row, 0).text())
            db.execute_query("DELETE FROM fields WHERE id = ?", (field_id,))
            self.load_fields()