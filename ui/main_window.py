import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QTabWidget,
                             QGroupBox, QMessageBox, QStyleFactory)
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QActionGroup, QAction

from logic.file_processor import FileProcessor
from palettes import HighContrastDarkPalette, HighContrastLightPalette
from logic.history_manager import HistoryManager
from logic.group_manager import GroupManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.settings = QSettings("YourCompany", "FileProcessor")
        self.contrast_mode = "normal"

        # Инициализация менеджеров
        self.history_manager = HistoryManager(self)
        self.group_manager = GroupManager(self)

        self.initUI()
        self.load_settings()

    def initUI(self):
        self.setWindowTitle('File Processor')
        self.setGeometry(100, 100, 900, 700)

        # Центральный виджет
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)

        # Вкладка обработки файлов
        self.processing_tab = self.create_processing_tab()
        central_widget.addTab(self.processing_tab, "Обработка файлов")

        # Вкладка истории
        history_tab = self.history_manager.create_history_tab()
        central_widget.addTab(history_tab, "История обработки")

        # Вкладка групп
        groups_tab = self.group_manager.create_groups_tab()
        central_widget.addTab(groups_tab, "Управление группами")

        # Меню
        self.create_menu()

        # Применяем начальные стили
        self.apply_styles()

    def create_processing_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Группа для выбора файла
        file_group = QGroupBox("Выбор файла")
        file_layout = QVBoxLayout()

        file_selector_layout = QHBoxLayout()
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setWordWrap(True)
        btn_choose = QPushButton("Выбрать файл")
        btn_choose.clicked.connect(self.choose_file)
        file_selector_layout.addWidget(self.file_label, 4)
        file_selector_layout.addWidget(btn_choose, 1)

        file_layout.addLayout(file_selector_layout)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # Группа для обработки
        process_group = QGroupBox("Обработка")
        process_layout = QVBoxLayout()
        btn_process = QPushButton("Обработать файл")
        btn_process.clicked.connect(self.process_file)
        process_layout.addWidget(btn_process)
        process_group.setLayout(process_layout)
        layout.addWidget(process_group)

        # Группа для результата
        result_group = QGroupBox("Результат обработки")
        result_layout = QVBoxLayout()
        self.result_label = QLabel("Результат: ")
        self.result_label.setWordWrap(True)
        result_layout.addWidget(self.result_label)
        result_group.setLayout(result_layout)
        layout.addWidget(result_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget

    def create_menu(self):
        menubar = self.menuBar()

        # Меню режимов контрастности
        contrast_menu = menubar.addMenu('Режим контрастности')

        self.normal_mode_action = QAction('Обычный режим', self)
        self.normal_mode_action.setCheckable(True)
        self.normal_mode_action.setChecked(True)
        self.normal_mode_action.triggered.connect(lambda: self.set_contrast_mode("normal"))
        contrast_menu.addAction(self.normal_mode_action)

        self.dark_contrast_action = QAction('Темная высокая контрастность', self)
        self.dark_contrast_action.setCheckable(True)
        self.dark_contrast_action.triggered.connect(lambda: self.set_contrast_mode("dark"))
        contrast_menu.addAction(self.dark_contrast_action)

        self.light_contrast_action = QAction('Светлая высокая контрастность', self)
        self.light_contrast_action.setCheckable(True)
        self.light_contrast_action.triggered.connect(lambda: self.set_contrast_mode("light"))
        contrast_menu.addAction(self.light_contrast_action)

        # Создаем группу действий для обеспечения взаимоисключающего выбора
        self.contrast_action_group = QActionGroup(self)
        self.contrast_action_group.addAction(self.normal_mode_action)
        self.contrast_action_group.addAction(self.dark_contrast_action)
        self.contrast_action_group.addAction(self.light_contrast_action)
        self.contrast_action_group.setExclusive(True)

    def choose_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if filepath:
            self.current_file = filepath
            self.file_label.setText(f"Выбран файл: {os.path.basename(filepath)}")

    def process_file(self):
        if self.current_file and os.path.exists(self.current_file):
            result = FileProcessor.process_file(self.current_file)
            self.result_label.setText(f"Результат: {result}")

            # Добавление в историю
            history_item = {
                'file': os.path.basename(self.current_file),
                'full_path': self.current_file,
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'result': result,
                'group': 'Без группы',
                'id': len(self.history_manager.history)
            }
            self.history_manager.add_to_history(history_item)
            self.save_settings()
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите файл")

    def set_contrast_mode(self, mode):
        self.contrast_mode = mode
        self.apply_styles()
        self.save_settings()

    def apply_styles(self):
        if self.contrast_mode == "dark":
            # Применяем темную высококонтрастную палитру
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            app.setPalette(HighContrastDarkPalette.get_palette())

            # Дополнительные стили для темной высокой контрастности
            style = """
            QMainWindow, QWidget {
                background-color: black;
                color: yellow;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid yellow;
                margin-top: 1ex;
                padding-top: 1ex;
                color: yellow;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: black;
                color: yellow;
            }
            QPushButton {
                background-color: black;
                color: yellow;
                border: 2px solid yellow;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: yellow;
                color: black;
            }
            QPushButton:pressed {
                background-color: #cccc00;
                color: black;
            }
            QTableWidget {
                gridline-color: yellow;
                background-color: black;
                color: yellow;
                border: 1px solid yellow;
            }
            QHeaderView::section {
                background-color: black;
                color: yellow;
                padding: 5px;
                border: 1px solid yellow;
                font-weight: bold;
            }
            QListWidget {
                background-color: black;
                color: yellow;
                border: 1px solid yellow;
            }
            QListWidget::item:selected {
                background-color: yellow;
                color: black;
            }
            QLineEdit, QComboBox {
                background-color: black;
                color: yellow;
                border: 1px solid yellow;
                padding: 2px;
            }
            QTabWidget::pane {
                border: 2px solid yellow;
                background-color: black;
            }
            QTabBar::tab {
                background-color: black;
                color: yellow;
                border: 1px solid yellow;
                padding: 8px;
            }
            QTabBar::tab:selected {
                background-color: yellow;
                color: black;
            }
            QMenu {
                background-color: black;
                color: yellow;
                border: 1px solid yellow;
            }
            QMenu::item:selected {
                background-color: yellow;
                color: black;
            }
            """
            app.setStyleSheet(style)

        elif self.contrast_mode == "light":
            # Применяем светлую высококонтрастную палитру
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            app.setPalette(HighContrastLightPalette.get_palette())

            # Дополнительные стили для светлой высокой контрастности
            style = """
            QMainWindow, QWidget {
                background-color: white;
                color: black;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid black;
                margin-top: 1ex;
                padding-top: 1ex;
                color: black;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: white;
                color: black;
                border: 2px solid black;
                padding: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: black;
                color: white;
            }
            QPushButton:pressed {
                background-color: #333333;
                color: white;
            }
            QTableWidget {
                gridline-color: black;
                background-color: white;
                color: black;
                border: 1px solid black;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
                border: 1px solid black;
                font-weight: bold;
            }
            QListWidget {
                background-color: white;
                color: black;
                border: 1px solid black;
            }
            QListWidget::item:selected {
                background-color: black;
                color: white;
            }
            QLineEdit, QComboBox {
                background-color: white;
                color: black;
                border: 1px solid black;
                padding: 2px;
            }
            QTabWidget::pane {
                border: 2px solid black;
                background-color: white;
            }
            QTabBar::tab {
                background-color: white;
                color: black;
                border: 1px solid black;
                padding: 8px;
            }
            QTabBar::tab:selected {
                background-color: black;
                color: white;
            }
            QMenu {
                background-color: white;
                color: black;
                border: 1px solid black;
            }
            QMenu::item:selected {
                background-color: black;
                color: white;
            }
            """
            app.setStyleSheet(style)

        else:
            # Обычный режим - возвращаем стандартную палитру и стили
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")
            app.setStyle(QStyleFactory.create("Fusion"))

    def save_settings(self):
        self.settings.setValue("contrast_mode", self.contrast_mode)

        # Сохраняем настройки из менеджеров
        history_settings = self.history_manager.save_settings()
        group_settings = self.group_manager.save_settings()

        self.settings.setValue("history", json.dumps(history_settings))
        self.settings.setValue("groups", json.dumps(group_settings))

    def load_settings(self):
        # Загрузка настроек режима контрастности
        contrast_mode = self.settings.value("contrast_mode", "normal")
        self.contrast_mode = contrast_mode

        # Устанавливаем правильное действие как выбранное
        if contrast_mode == "dark":
            self.dark_contrast_action.setChecked(True)
        elif contrast_mode == "light":
            self.light_contrast_action.setChecked(True)
        else:
            self.normal_mode_action.setChecked(True)

        # Загрузка настроек истории
        history_json = self.settings.value("history", "{}")
        try:
            history_settings = json.loads(history_json)
            self.history_manager.load_settings(history_settings)
        except:
            pass

        # Загрузка настроек групп
        groups_json = self.settings.value("groups", "{}")
        try:
            group_settings = json.loads(groups_json)
            self.group_manager.load_settings(group_settings)
        except:
            pass

        # Обновляем интерфейс
        self.history_manager.update_history_table()
        self.history_manager.update_group_filters()

        # Применяем стили после загрузки настроек
        self.apply_styles()