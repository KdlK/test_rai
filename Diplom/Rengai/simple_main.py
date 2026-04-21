"""Simple Rengai Chat - minimal version."""
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QPushButton, QLabel, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Rengai Chat")
window.setMinimumSize(600, 500)

central = QWidget()
window.setCentralWidget(central)

layout = QVBoxLayout(central)
layout.setContentsMargins(0, 0, 0, 0)

scroll = QScrollArea()
scroll.setWidgetResizable(True)
scroll.setStyleSheet("background-color: #eef2f6;")
scroll_container = QWidget()
scroll_layout = QVBoxLayout(scroll_container)
scroll_layout.addWidget(QLabel("Привет! Напишите сообщение..."))
scroll.setWidget(scroll_container)
layout.addWidget(scroll, 1)

input_area = QWidget()
input_area.setStyleSheet("background-color: white; border-top: 1px solid #d1d5db;")
input_layout = QHBoxLayout(input_area)
input_layout.setContentsMargins(16, 12, 16, 12)

input_field = QPlainTextEdit()
input_field.setFixedHeight(44)
input_field.setPlaceholderText("Сообщение...")
input_field.setStyleSheet("""
    background-color: #eff3f5;
    border-radius: 22px;
    padding: 10px 16px;
    font-size: 14px;
""")
input_layout.addWidget(input_field, 1)

send_btn = QPushButton("✈")
send_btn.setFixedSize(44, 44)
send_btn.setStyleSheet("""
    background-color: #40c057;
    border-radius: 22px;
    color: white;
    font-size: 18px;
""")
input_layout.addWidget(send_btn)

tim_check = QCheckBox("ТИМ")
input_layout.addWidget(tim_check)

clear_btn = QPushButton("Очистить")
clear_btn.setStyleSheet("""
    background-color: #f3f4f6;
    border-radius: 18px;
    padding: 8px 16px;
""")
input_layout.addWidget(clear_btn)

layout.addWidget(input_area)

window.show()
print("Окно открыто!")
app.exec()