from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QTableWidget, QTableWidgetItem, QMessageBox, 
                             QDialog, QFormLayout, QLineEdit, QComboBox, 
                             QTextEdit, QHeaderView, QLabel, QDateEdit, 
                             QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt, QDate
from database import db
from models import Expense

class ExpenseDialog(QDialog):
    def __init__(self, expense=None, parent=None):
        super().__init__(parent)
        self.expense = expense
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Редагування витрат" if self.expense else "Додати витрати")
        self.setFixedWidth(500)
        
        layout = QFormLayout()
        
        # Отримання списків полів і культур
        fields = db.fetch_all("SELECT id, name FROM fields")
        crops = db.fetch_all("SELECT id, name FROM crops")
        
        self.field_combo = QComboBox()
        self.field_combo.addItem("-- Не обрано --", None)
        for field in fields:
            self.field_combo.addItem(f"{field[0]}. {field[1]}", field[0])
        
        if self.expense and self.expense.field_id:
            index = self.field_combo.findData(self.expense.field_id)
            if index >= 0:
                self.field_combo.setCurrentIndex(index)
        
        layout.addRow("Поле:", self.field_combo)
        
        self.crop_combo = QComboBox()
        self.crop_combo.addItem("-- Не обрано --", None)
        for crop in crops:
            self.crop_combo.addItem(f"{crop[0]}. {crop[1]}", crop[0])
        
        if self.expense and self.expense.crop_id:
            index = self.crop_combo.findData(self.expense.crop_id)
            if index >= 0:
                self.crop_combo.setCurrentIndex(index)
        
        layout.addRow("Культура:", self.crop_combo)
        
        self.type_combo = QComboBox()
        expense_types = [
            ("Насіння", "seeds"),
            ("Паливо", "fuel"),
            ("Добрива", "fertilizers"),
            ("Хімікати", "chemicals"),
            ("Робоча сила", "labor"),
            ("Техніка", "equipment"),
            ("Інше", "other")
        ]
        
        for display_name, value in expense_types:
            self.type_combo.addItem(display_name, value)
        
        if self.expense:
            index = self.type_combo.findData(self.expense.expense_type)
            if index >= 0:
                self.type_combo.setCurrentIndex(index)
        
        layout.addRow("Тип витрат:", self.type_combo)
        
        self.amount_spin = QDoubleSpinBox()
        self.amount_spin.setRange(0, 1000000)
        self.amount_spin.setPrefix("₴ ")
        self.amount_spin.setDecimals(2)
        if self.expense:
            self.amount_spin.setValue(self.expense.amount)
        layout.addRow("Сума (грн):", self.amount_spin)
        
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0, 1000000)
        self.quantity_spin.setDecimals(2)
        if self.expense:
            self.quantity_spin.setValue(self.expense.quantity)
        layout.addRow("Кількість:", self.quantity_spin)
        
        self.unit_input = QLineEdit()
        if self.expense:
            self.unit_input.setText(self.expense.unit)
        layout.addRow("Одиниця:", self.unit_input)
        
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        if self.expense and self.expense.date:
            self.date_edit.setDate(QDate.fromString(self.expense.date, "yyyy-MM-dd"))
        layout.addRow("Дата:", self.date_edit)
        
        self.description_input = QTextEdit()
        if self.expense:
            self.description_input.setText(self.expense.description)
        self.description_input.setMaximumHeight(80)
        layout.addRow("Опис:", self.description_input)
        
        # Розрахунок загальної вартості
        self.total_label = QLabel("Загальна вартість: 0.00 ₴")
        layout.addRow(self.total_label)
        
        # Кнопки
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_expense)
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addRow(button_layout)
        
        self.setLayout(layout)
        
        # Підключення сигналів для розрахунку
        self.amount_spin.valueChanged.connect(self.update_total)
        self.quantity_spin.valueChanged.connect(self.update_total)
    
    def update_total(self):
        total = self.amount_spin.value() * self.quantity_spin.value()
        self.total_label.setText(f"Загальна вартість: {total:.2f} ₴")
    
    def save_expense(self):
        total_cost = self.amount_spin.value() * self.quantity_spin.value()
        
        field_id = self.field_combo.currentData()
        crop_id = self.crop_combo.currentData()
        
        if self.expense:
            db.execute_query(
                """UPDATE expenses SET field_id=?, crop_id=?, expense_type=?, 
                   amount=?, quantity=?, unit=?, total_cost=?, date=?, description=? 
                   WHERE id=?""",
                (field_id, crop_id, self.type_combo.currentData(),
                 self.amount_spin.value(), self.quantity_spin.value(),
                 self.unit_input.text(), total_cost,
                 self.date_edit.date().toString("yyyy-MM-dd"),
                 self.description_input.toPlainText(),
                 self.expense.id)
            )
        else:
            db.execute_query(
                """INSERT INTO expenses 
                   (field_id, crop_id, expense_type, amount, quantity, unit, 
                    total_cost, date, description) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (field_id, crop_id, self.type_combo.currentData(),
                 self.amount_spin.value(), self.quantity_spin.value(),
                 self.unit_input.text(), total_cost,
                 self.date_edit.date().toString("yyyy-MM-dd"),
                 self.description_input.toPlainText())
            )
        
        self.accept()

class ExpensesModule(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_expenses()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Заголовок
        title_label = QLabel("Облік витрат")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Фільтри
        filter_layout = QHBoxLayout()
        
        self.filter_type_combo = QComboBox()
        self.filter_type_combo.addItems(["Всі типи", "Насіння", "Паливо", "Добрива", 
                                         "Хімікати", "Робоча сила", "Техніка", "Інше"])
        self.filter_type_combo.currentTextChanged.connect(self.load_expenses)
        
        self.year_combo = QComboBox()
        self.year_combo.addItems(["Всі роки", "2024", "2023", "2022"])
        self.year_combo.currentTextChanged.connect(self.load_expenses)
        
        filter_layout.addWidget(QLabel("Тип витрат:"))
        filter_layout.addWidget(self.filter_type_combo)
        filter_layout.addWidget(QLabel("Рік:"))
        filter_layout.addWidget(self.year_combo)
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Кнопки управління
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Додати витрати")
        self.add_btn.clicked.connect(self.add_expense)
        
        self.edit_btn = QPushButton("✏️ Редагувати")
        self.edit_btn.clicked.connect(self.edit_expense)
        
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.delete_btn.clicked.connect(self.delete_expense)
        
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # Таблиця витрат
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Поле", "Культура", "Тип", "Сума", "Кількість", "Загальна вартість", "Дата"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.table)
        
        # Статистика
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; padding: 5px; font-weight: bold;")
        layout.addWidget(self.stats_label)
        
        self.setLayout(layout)
    
    def load_expenses(self):
        filter_type = self.filter_type_combo.currentText()
        year = self.year_combo.currentText()
        
        query = """SELECT e.id, f.name, c.name, e.expense_type, 
                   e.amount, e.quantity, e.total_cost, e.date 
                   FROM expenses e
                   LEFT JOIN fields f ON e.field_id = f.id
                   LEFT JOIN crops c ON e.crop_id = c.id
                   WHERE 1=1"""
        
        params = []
        
        if filter_type != "Всі типи":
            type_map = {
                "Насіння": "seeds",
                "Паливо": "fuel",
                "Добрива": "fertilizers",
                "Хімікати": "chemicals",
                "Робоча сила": "labor",
                "Техніка": "equipment",
                "Інше": "other"
            }
            query += " AND e.expense_type = ?"
            params.append(type_map.get(filter_type, filter_type))
        
        if year != "Всі роки":
            query += " AND strftime('%Y', e.date) = ?"
            params.append(year)
        
        query += " ORDER BY e.date DESC"
        
        expenses = db.fetch_all(query, tuple(params))
        self.table.setRowCount(len(expenses))
        
        total_expenses = 0
        type_names = {
            "seeds": "Насіння",
            "fuel": "Паливо",
            "fertilizers": "Добрива",
            "chemicals": "Хімікати",
            "labor": "Робоча сила",
            "equipment": "Техніка",
            "other": "Інше"
        }
        
        for row_idx, expense in enumerate(expenses):
            total_expenses += expense[6] if expense[6] else 0
            
            for col_idx in range(8):
                if col_idx == 0:  # ID
                    value = str(expense[0])
                elif col_idx == 3:  # Тип витрат
                    value = type_names.get(expense[3], expense[3])
                elif col_idx in [4, 5, 6]:  # Суми
                    value = f"{expense[col_idx]:.2f}" if expense[col_idx] else "0.00"
                    if col_idx == 6:  # Загальна вартість
                        value += " ₴"
                elif col_idx == 7:  # Дата
                    value = expense[7] if expense[7] else ""
                else:  # Назви полів та культур
                    value = expense[col_idx] if expense[col_idx] else "--"
                
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row_idx, col_idx, item)
        
        self.stats_label.setText(f"Загальна сума витрат: {total_expenses:.2f} ₴ | Кількість записів: {len(expenses)}")
    
    def add_expense(self):
        dialog = ExpenseDialog()
        if dialog.exec():
            self.load_expenses()
    
    def edit_expense(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для редагування")
            return
        
        row = selected[0].row()
        expense_id = int(self.table.item(row, 0).text())
        
        expense_data = db.fetch_one("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        if expense_data:
            expense = Expense(
                id=expense_data[0],
                field_id=expense_data[1],
                crop_id=expense_data[2],
                expense_type=expense_data[3],
                amount=expense_data[4],
                quantity=expense_data[5],
                unit=expense_data[6],
                total_cost=expense_data[7],
                date=expense_data[8],
                description=expense_data[9]
            )
            
            dialog = ExpenseDialog(expense, self)
            if dialog.exec():
                self.load_expenses()
    
    def delete_expense(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Помилка", "Виберіть запис для видалення")
            return
        
        reply = QMessageBox.question(
            self, "Підтвердження",
            "Видалити обраний запис витрат?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            row = selected[0].row()
            expense_id = int(self.table.item(row, 0).text())
            db.execute_query("DELETE FROM expenses WHERE id = ?", (expense_id,))
            self.load_expenses()