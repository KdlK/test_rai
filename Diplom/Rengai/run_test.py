"""Simple test to verify UI works."""
import sys
import os

os.environ['QT_QPA_PLATFORM'] = 'windows'

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QCheckBox
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Test UI")
window.setMinimumSize(600, 400)

central = QWidget()
layout = QVBoxLayout(central)

layout.addWidget(QLabel("Это тест!"))

input_field = QLineEdit()
input_field.setPlaceholderText("Введите сообщение...")
input_field.setStyleSheet("background-color: white; padding: 10px; border-radius: 10px;")
layout.addWidget(input_field)

checkbox = QCheckBox("ТИМ-помощник")
layout.addWidget(checkbox)

btn = QPushButton("Отправить")
btn.setStyleSheet("background-color: #40c057; color: white; padding: 10px; border-radius: 20px;")
layout.addWidget(btn)

window.setCentralWidget(central)
window.show()

print("Window should be visible now!")
sys.exit(app.exec())