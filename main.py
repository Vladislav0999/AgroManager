import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Створення сплеш-скріну
    splash_pix = QPixmap(400, 300)
    splash_pix.fill(Qt.GlobalColor.green)
    
    splash = QSplashScreen(splash_pix)
    splash.showMessage("Завантаження AgroFarm Manager...\n"
                      "Ініціалізація бази даних...",
                      Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                      Qt.GlobalColor.white)
    splash.show()
    
    # Оновлення сплеш-скріну
    app.processEvents()
    
    # Створення головного вікна
    window = MainWindow()
    
    # Затримка перед показом головного вікна
    QTimer.singleShot(1500, lambda: finish_startup(splash, window))
    
    sys.exit(app.exec())

def finish_startup(splash, window):
    window.show()
    splash.finish(window)
    
    # Показати привітання
    from PyQt6.QtWidgets import QMessageBox
    QMessageBox.information(window, "Ласкаво просимо!", 
        "AgroFarm Manager успішно запущено!\n\n"
        "Для початку роботи виберіть потрібний модуль з панелі навігації.")

if __name__ == "__main__":
    # Перевірка та створення необхідних папок
    os.makedirs("exports", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    main()