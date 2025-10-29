import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QFileDialog, QTabWidget,
                             QGroupBox, QMessageBox, QStyleFactory,
                             QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QActionGroup, QAction, QFont

import config
from logic.file_processor import FileProcessor
from ui.palettes import HighContrastDarkPalette, HighContrastLightPalette
from logic.history_manager import HistoryManager
from logic.group_manager import GroupManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.scenario_file = None
        self.xsd_file = None
        self.output_dir = None
        self.settings = QSettings(config.APP_DB_NAME, "FileProcessor")
        self.contrast_mode = "normal"

        # Инициализация менеджеров
        self.history_manager = HistoryManager(self)
        self.group_manager = GroupManager(self)

        self.initUI()
        self.load_settings()

    def initUI(self):
        self.setWindowTitle('ГосМост')
        self.setGeometry(100, 100, 900, 600)

        # Центральный виджет
        central_widget = QTabWidget()
        self.setCentralWidget(central_widget)

        # Вкладка генерации VM шаблона
        self.processing_tab = self.create_processing_tab()
        central_widget.addTab(self.processing_tab, "Создать шаблон")

        # Вкладка истории
        history_tab = self.history_manager.create_history_tab()
        central_widget.addTab(history_tab, "История обработки")

        # Вкладка проектов
        groups_tab = self.group_manager.create_groups_tab()
        central_widget.addTab(groups_tab, "Управлять проектами")

        # Меню
        self.create_menu()

        # Применяем начальные стили
        self.apply_styles()

    def create_processing_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # Группа для выбора файлов
        files_group = QGroupBox("Выбор файлов для генерации адаптивного VM шаблона")
        files_group.setObjectName("file_group")
        files_group.setStyleSheet("#file_group{font-size: 14pt; margin-top: 15px;}")
        files_layout = QVBoxLayout()

        # Файл сценария
        scenario_layout = QHBoxLayout()
        self.scenario_label = QLabel("1. Файл json: не выбран")
        self.scenario_label.setWordWrap(True)
        btn_choose_scenario = QPushButton("Выбрать json файл")
        btn_choose_scenario.clicked.connect(lambda: self.choose_file('scenario'))
        scenario_layout.addWidget(self.scenario_label, 4)
        scenario_layout.addWidget(btn_choose_scenario, 1)
        files_layout.addLayout(scenario_layout)
        files_layout.setSpacing(15)

        # XSD файл
        xsd_layout = QHBoxLayout()
        self.xsd_label = QLabel("2. XSD схема: не выбрана")
        self.xsd_label.setWordWrap(True)
        btn_choose_xsd = QPushButton("Выбрать XSD файл")
        btn_choose_xsd.clicked.connect(lambda: self.choose_file('xsd'))
        xsd_layout.addWidget(self.xsd_label, 4)
        xsd_layout.addWidget(btn_choose_xsd, 1)
        files_layout.addLayout(xsd_layout)

        # Директория для сохранения
        output_layout = QHBoxLayout()
        self.output_label = QLabel(
            "3. Директория для сохранения: не выбрана (по умолчанию: текущая папка, указывать необязательно)")
        self.output_label.setWordWrap(True)
        btn_choose_output = QPushButton("Выбрать директорию")
        btn_choose_output.clicked.connect(self.choose_output_dir)
        output_layout.addWidget(self.output_label, 4)
        output_layout.addWidget(btn_choose_output, 1)
        files_layout.addLayout(output_layout)

        files_group.setLayout(files_layout)
        layout.addWidget(files_group)

        process_group = QGroupBox("4. Генерация шаблонов")
        process_layout = QVBoxLayout()

        process_buttons_layout = QHBoxLayout()
        btn_process = QPushButton("Сгенерировать VM")
        btn_process.clicked.connect(self.generate_vm_template)

        btn_clear = QPushButton("Очистить выбор")
        btn_clear.clicked.connect(self.clear_files)

        process_buttons_layout.addWidget(btn_process)
        process_buttons_layout.addWidget(btn_clear)
        process_layout.addLayout(process_buttons_layout)
        process_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        process_group.setLayout(process_layout)
        layout.addWidget(process_group)

        # Группа для результата
        result_group = QGroupBox("Результат генерации")
        result_layout = QVBoxLayout()


        self.result_info = QLabel("Пусто")
        self.result_info.setWordWrap(True)
        self.result_info.setStyleSheet("font-size: 11pt)")
        result_layout.addWidget(self.result_info)

        result_group.setLayout(result_layout)
        layout.addWidget(result_group)
        layout.setStretch(2, 1)
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

    def choose_file(self, file_type):
        file_filter = "Все файлы (*);;JSON files (*.json);;Text files (*.txt)" if file_type in ['scenario',
                                                                                                'service'] else "XSD files (*.xsd);;Text files (*.txt);;Все файлы (*)"
        filepath, _ = QFileDialog.getOpenFileName(self, f"Выберите {file_type} файл", "", file_filter)

        if filepath:
            if file_type == 'scenario':
                self.scenario_file = filepath
                self.scenario_label.setText(f"Файл сценария: {os.path.basename(filepath)}")
            elif file_type == 'service':
                self.service_file = filepath
                self.service_label.setText(f"Файл схемы услуги: {os.path.basename(filepath)}")
            elif file_type == 'xsd':
                self.xsd_file = filepath
                self.xsd_label.setText(f"XSD схема: {os.path.basename(filepath)}")

    def choose_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Выберите директорию для сохранения")
        if dir_path:
            self.output_dir = dir_path
            self.output_label.setText(f"Директория для сохранения: {dir_path}")

    def clear_files(self):
        self.scenario_file = None
        self.xsd_file = None
        self.output_dir = None
        self.scenario_label.setText("Файл json: не выбран")
        self.xsd_label.setText("XSD схема: не выбрана")
        self.output_label.setText("Директория для сохранения: не выбрана (по умолчанию: текущая папка)")
        self.result_info.setText("Пусто")

    def generate_vm_template(self):
        if not all([self.scenario_file, self.xsd_file]):
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите все три файла")
            return

        try:
            # Создаем папку для сохранения, если она не существует
            output_path = self.output_dir
            if output_path and not os.path.exists(output_path):
                os.makedirs(output_path, exist_ok=True)

            # Генерация VM шаблонов
            result = FileProcessor.build_vm_template(
                self.scenario_file,
                self.xsd_file,
                output_path
            )

            if result['success']:
                raw_path = result['raw_output_path']
                filled_path = result['filled_output_path']

                info_text = (
                    f"<b>VM шаблоны успешно сгенерированы!</b><br>"
                    f"Корневой элемент: {result['root_element']}<br>"
                    f"template_raw.vm: <a href='file:///{raw_path}'>{raw_path}</a><br>"
                    f"template_generated.vm: <a href='file:///{filled_path}'>{filled_path}</a><br>"
                    f"Выполнено замен: {result['replacements_count']}<br>"
                    f"Структура: {result['structure_summary']}"
                )

                self.result_info.setTextFormat(Qt.TextFormat.RichText)
                self.result_info.setTextInteractionFlags(
                    Qt.TextInteractionFlag.TextBrowserInteraction
                )
                self.result_info.setOpenExternalLinks(True)
                self.result_info.setText(info_text)

                # Создаем строку с файлами для отображения в таблице
                files_list = [
                    f"{os.path.basename(self.scenario_file)}, {os.path.basename(self.xsd_file)}",
                    f"{os.path.basename(result['raw_output_path'])}"
                ]
                files_display = "\n".join(files_list)

                # Добавление в историю
                history_item = {
                    'file': files_display,
                    'files': {
                        'input': [
                            {'type': 'scenario', 'path': self.scenario_file,
                             'name': os.path.basename(self.scenario_file)},
                            {'type': 'xsd', 'path': self.xsd_file, 'name': os.path.basename(self.xsd_file)}
                        ],
                        'output': [
                            {'type': 'raw_vm', 'path': result['raw_output_path'],
                             'name': os.path.basename(result['raw_output_path'])},
                            {'type': 'filled_vm', 'path': result['filled_output_path'],
                             'name': os.path.basename(result['filled_output_path'])}
                        ]
                    },
                    'full_path': result['raw_output_path'],
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'result': f"Успешно сгенерированы ({result['replacements_count']} замен)",
                    'group': 'Черновик',
                    'id': len(self.history_manager.history)
                }
                self.history_manager.add_to_history(history_item)
                self.save_settings()

                QMessageBox.information(self, "Успех",
                                        f"VM шаблоны успешно сгенерированы!\n\n"
                                        f"template_raw.vm: {result['raw_output_path']}\n"
                                        f"template_generated.vm: {result['filled_output_path']}")
            else:
                error_msg = f"Ошибка при генерации VM шаблонов: {result['error']}"
                self.result_info.setText(error_msg)

                QMessageBox.critical(self, "Ошибка", error_msg)

        except Exception as e:
            error_msg = f"Неожиданная ошибка: {str(e)}"
            self.result_info.setText(error_msg)
            QMessageBox.critical(self, "Ошибка", error_msg)

    def set_contrast_mode(self, mode):
        self.contrast_mode = mode
        self.apply_styles()
        self.save_settings()

    def apply_styles(self):
        if self.contrast_mode == "dark":
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            app.setPalette(HighContrastDarkPalette.get_palette())

            style = """
            QMainWindow, QWidget {
                background-color: black;
                color: yellow;
                font-size: 13pt;
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
            QTextEdit {
                background-color: black;
                color: yellow;
                border: 1px solid yellow;
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
                font-size: 14pt;
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
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            app.setPalette(HighContrastLightPalette.get_palette())

            style = """
            QMainWindow, QWidget {
                background-color: white;
                color: black;
                font-size: 13pt;
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
            QTextEdit {
                background-color: white;
                color: black;
                border: 1px solid black;
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
                font-size: 14pt;
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
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("QTabBar::tab {font-size: 14pt;} QWidget{font-size: 13pt;}")
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