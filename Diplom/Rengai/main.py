"""Main PyQt6 application for Rengai Chat."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QEvent, QPoint
from PyQt6.QtGui import QAction, QFont, QColor, QIcon, QPixmap, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from Rengai.config import config
from Rengai.context import context_manager
from Rengai.llm_client import llm_client


def get_system_prompt(tim_mode: bool = False) -> str:
    """Формирует system prompt для LLM."""
    from Rengai.config import read_all_resources
    
    all_content = read_all_resources()
    
    base_prompt = f"""Ты - ИИ-ассистент для помощи пользователям в работе с Renga (программа для BIM-проектирования).
Твоя задача - отвечать на вопросы пользователей, используя информацию из базы знаний.
{all_content}

Инструкции:
1. Используй информацию из файлов выше при ответах.
2. Если информации недостаточно, честно скажи об этом.
3. Отвечай на русском языке."""

    if tim_mode:
        skills = list(config.skills_dir.glob("*.py"))
        skills_info = "\n".join(f"- {s.stem}" for s in skills if s.name != "__init__.py") if skills else "Нет доступных навыков"
        
        return f"""{base_prompt}

РЕЖИМ ТИМ-ПОМОЩНИКА АКТИВЕН!

Доступные функции взаимодействия с Renga:
{skills_info}

Когда пользователь просит выполнить действие с Renga (например "запусти renga", "открой ренга", "посчитай объем"),
ты ДОЛЖЕН вернуть JSON в таком формате:
{{"action": "название_функции", "args": {{"параметр1": "значение1"}}}}

Примеры:
- "запусти renga" -> {{"action": "open_renga", "args": {{}}}}
- "посчитай объем стен" -> {{"action": "calculate_volume", "args": {{"category": "walls"}}}}
"""
    return base_prompt


class CommandExecutor:
    """Выполняет команды Renga."""

    @staticmethod
    def execute(action: str, args: dict) -> str:
        """Выполняет команду."""
        try:
            if action == "open_renga":
                from renga_api.skills.app import open_renga as renga_open
                result = renga_open(mode='new')
                return f"Renga запущена! Версия: {result.get('version', 'unknown')}"
            
            elif action == "calculate_volume":
                try:
                    from Rengai.skills.calculate_volume import calculate_volume
                    category = args.get("category", "walls")
                    if category is None:
                        return "Не удалось определить категорию элементов"
                    result = calculate_volume(category)
                    if not result.get("success", False):
                        return result.get("error", "Не удалось выполнить расчёт")
                    return f"Объём: {result.get('total_volume', 0):.3f} м³ ({result.get('element_count', 0)} элементов)\n{result.get('message', '')}"
                except Exception as e:
                    return f"Ошибка расчёта: {str(e)}"

            elif action == "export_ifc":
                try:
                    from Rengai.skills.export_ifc import export_ifc
                    result = export_ifc()
                    if result.get("success"):
                        return f"IFC экспорт: {result.get('message', 'Готово')}"
                    else:
                        return f"Ошибка: {result.get('error', 'Неизвестная ошибка')}"
                except Exception as e:
                    return f"Ошибка экспорта: {str(e)}"
            
            else:
                return f"Неизвестная команда: {action}"
        except Exception as e:
            return f"Ошибка: {str(e)}"


class ChatWorker(QThread):
    """Worker thread for async LLM chat operations."""

    chunk_received = pyqtSignal(str)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, messages, tim_mode: bool = False, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._messages = messages
        self._tim_mode = tim_mode

    def run(self) -> None:
        try:
            full_response = ""
            for chunk in llm_client.chat_stream(self._messages):
                full_response += chunk
                self.chunk_received.emit(chunk)
            self.finished.emit(full_response)
        except Exception as e:
            self.error_occurred.emit(str(e))


class ChatWidget(QWidget):
    """Main chat interface widget."""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._worker: Optional[ChatWorker] = None
        self._current_response = ""
        self._tim_mode = False
        self._setup_ui()

    def set_tim_mode(self, enabled: bool) -> None:
        self._tim_mode = enabled

    def _toggle_tim_mode(self, state: int) -> None:
        self._tim_mode = (state == 2)
        with open("rengai_debug.log", "a") as f:
            f.write(f"DEBUG: TIM mode={self._tim_mode}, state={state}\n")
        context_manager.clear_history()

    def _setup_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Chat scroll area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("background-color: #eef2f6; border: none;")
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(16, 16, 16, 16)
        self.chat_layout.setSpacing(12)
        self.chat_layout.addStretch()
        self.chat_scroll.setWidget(self.chat_container)
        main_layout.addWidget(self.chat_scroll, 1)

        # Input area
        self.input_container = QWidget()
        self.input_container.setStyleSheet("background-color: white; border-top: 1px solid #d1d5db;")
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(12, 10, 12, 10)
        self.input_layout.setSpacing(10)

        # Input field
        self.input_field = QPlainTextEdit()
        self.input_field.setFixedHeight(44)
        self.input_field.setPlaceholderText("Сообщение...")
        self.input_field.setStyleSheet("""
            QPlainTextEdit {
                background-color: #eff3f5;
                color: #333333;
                font-size: 14px;
                border: none;
                border-radius: 22px;
                padding: 10px 16px;
            }
            QPlainTextEdit:focus {
                border: 1px solid #40c057;
            }
        """)
        self.input_layout.addWidget(self.input_field, 1)

        # Send button
        self.send_btn = QPushButton()
        self.send_btn.setFixedSize(44, 44)
        self._draw_send_icon()
        self.send_btn.clicked.connect(self._send_message)
        self.input_layout.addWidget(self.send_btn)

        # TIM checkbox
        self.tim_checkbox = QCheckBox("  ТИМ-помощник")
        self.tim_checkbox.setStyleSheet("""
            QCheckBox {
                color: #555555;
                font-size: 13px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid #d1d5db;
                background-color: #f3f4f6;
            }
            QCheckBox::indicator:checked {
                background-color: #40c057;
                border-color: #40c057;
            }
        """)
        self.tim_checkbox.stateChanged.connect(self._toggle_tim_mode)
        self.input_layout.addWidget(self.tim_checkbox)

        # Clear button
        self.clear_btn = QPushButton("Очистить")
        self.clear_btn.setFixedSize(80, 36)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f3f4f6;
                color: #6b7280;
                border: none;
                border-radius: 18px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                color: #374151;
            }
        """)
        self.clear_btn.clicked.connect(self._clear_history)
        self.input_layout.addWidget(self.clear_btn)

        main_layout.addWidget(self.input_container)

        self.input_field.installEventFilter(self)

    def _draw_send_icon(self) -> None:
        """Draw plane icon on send button."""
        self.send_btn.setText("✈")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #40c057;
                border-radius: 22px;
                border: none;
                color: white;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #37c24f;
            }
        """)

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:
        if obj == self.input_field and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return:
                modifiers = QApplication.keyboardModifiers()
                if modifiers == Qt.KeyboardModifier.ShiftModifier:
                    return False
                else:
                    self._send_message()
                    return True
        return super().eventFilter(obj, event)

    def _append_message(self, sender: str, message: str, is_user: bool = False) -> None:
        msg_widget = QWidget()
        layout = QVBoxLayout(msg_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        name = QLabel(sender)
        name.setStyleSheet("font-size: 12px; font-weight: 600;")
        if is_user:
            name.setStyleSheet(name.styleSheet() + "color: #5ac8a0; padding-left: 12px;")
            bubble_color = "#dcf8c6"
        else:
            name.setStyleSheet(name.styleSheet() + "color: #7c80a0; padding-left: 12px;")
            bubble_color = "#ffffff"
        layout.addWidget(name)

        bubble = QLabel(message)
        bubble.setWordWrap(True)
        bubble.setStyleSheet(f"""
            background-color: {bubble_color};
            color: #333333;
            font-size: 14px;
            padding: 10px 14px;
            border-radius: 16px;
        """)
        layout.addWidget(bubble)

        if is_user:
            h_layout = QHBoxLayout()
            h_layout.addStretch()
            h_layout.addWidget(msg_widget)
            self.chat_layout.addLayout(h_layout)
        else:
            self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)

        self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        )

    def _send_message(self) -> None:
        message = self.input_field.toPlainText().strip()
        if not message:
            return

        self.input_field.clear()
        self._append_message("Вы", message, is_user=True)
        context_manager.add_message("user", message)
        self._start_llm_request()

    def _start_llm_request(self) -> None:
        messages = context_manager.get_messages()
        
        # Add system prompt only if not already present
        has_system = any(m.get("role") == "system" for m in messages)
        if not has_system:
            system_prompt = get_system_prompt(self._tim_mode)
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Make a copy
        messages_to_send = list(messages)
        
        self._worker = ChatWorker(messages_to_send, self._tim_mode)
        self._worker.chunk_received.connect(self._on_chunk)
        self._worker.finished.connect(self._on_finished)
        self._worker.error_occurred.connect(self._on_error)
        
        self._current_response = ""
        self._append_message("Ассистент", "...", is_user=False)
        self._worker.start()

    def _on_chunk(self, chunk: str) -> None:
        self._current_response += chunk
        # Update last message
        if self.chat_layout.count() > 1:
            last = self.chat_layout.itemAt(self.chat_layout.count() - 2).widget()
            if last:
                for child in last.findChildren(QLabel):
                    if child.wordWrap():
                        current_text = child.text()
                        if current_text == "...":
                            child.setText(chunk)
                        else:
                            child.setText(current_text + chunk)
                        break

    def _on_finished(self, response: str) -> None:
        context_manager.add_message("assistant", response)
        
        # Update the "..." message with the full response
        if self.chat_layout.count() > 1:
            last = self.chat_layout.itemAt(self.chat_layout.count() - 2).widget()
            if last:
                for child in last.findChildren(QLabel):
                    if child.wordWrap():
                        child.setText(response)
                        break

        # Execute command if in TIM mode
        if self._tim_mode:
            action = None
            args = {}
            response_lower = response.lower()
            
            # Get user's last message
            user_message = ""
            messages = context_manager.get_messages()
            for msg in reversed(messages):
                if msg.get("role") == "user":
                    user_message = msg.get("content", "").lower()
                    break
            
            # Detect action from response
            if "export_ifc" in response or "ifc" in response:
                action = "export_ifc"
                self._append_message("Ассистент", "Обнаружен запрос на экспорт в IFC. Выполняю...", is_user=False)
                args = {}
            elif "open_renga" in response or "запусти" in response_lower:
                action = "open_renga"
                self._append_message("Ассистент", "Обнаружен запрос на запуск Renga. Выполняю...", is_user=False)
                args = {}
            elif "объём" in response_lower or "объем" in response_lower or "посчитай" in response_lower:
                action = "calculate_volume"
                from Rengai.skills.calculate_volume import detect_category_from_text
                category = detect_category_from_text(user_message)
                self._append_message("Ассистент", f"Обнаружен запрос на расчёт объёма ({category}). Выполняю...", is_user=False)
                args = {"category": category or "walls"}
            
            if action:
                try:
                    result = CommandExecutor.execute(action, args)
                    if "error" in result.lower() or "не могу" in result.lower() or "откройте" in result.lower():
                        self._append_message("Ошибка", result, is_user=False)
                    else:
                        self._append_message("Система", result, is_user=False)
                except Exception as e:
                    self._append_message("Ошибка", str(e), is_user=False)

    def _on_error(self, error: str) -> None:
        self._append_message("Ошибка", error, is_user=False)

    def _clear_history(self) -> None:
        reply = QMessageBox.question(
            self, "Очистить историю", "Вы уверены?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            while self.chat_layout.count() > 1:
                item = self.chat_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            context_manager.clear_history()


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Rengai Chat")
        self.setMinimumSize(600, 500)
        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.chat_widget = ChatWidget()
        layout.addWidget(self.chat_widget)


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor("#eef2f6"))
    app.setPalette(palette)
    
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
