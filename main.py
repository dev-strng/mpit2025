import sys
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QFileDialog,
                             QTabWidget, QTableWidget, QTableWidgetItem,
                             QHeaderView, QComboBox, QLineEdit, QMessageBox,
                             QCheckBox, QGroupBox, QMenu, QListWidget, QListWidgetItem,
                             QInputDialog, QStyleFactory)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QPalette, QColor, QAction, QFont, QActionGroup


class FileProcessor:
    @staticmethod
    def process_file(filepath):
        # Заглушка для обработки файла
        return f"Обработан {os.path.basename(filepath)} ({datetime.now().strftime('%H:%M:%S')})"


class HighContrastDarkPalette:
    @staticmethod
    def get_palette():
        palette = QPalette()
        # Темная высококонтрастная схема
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 0))  # Желтый текст
        palette.setColor(QPalette.ColorRole.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 255, 0))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        # Дополнительные цвета
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 0))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 255, 255))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(255, 0, 255))

        # Границы и тени
        palette.setColor(QPalette.ColorRole.Dark, QColor(255, 255, 0))
        palette.setColor(QPalette.ColorRole.Mid, QColor(128, 128, 0))
        palette.setColor(QPalette.ColorRole.Light, QColor(255, 255, 128))

        return palette


class HighContrastLightPalette:
    @staticmethod
    def get_palette():
        palette = QPalette()
        # Светлая высококонтрастная схема
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))  # Черный текст
        palette.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Button, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        # Дополнительные цвета
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        palette.setColor(QPalette.ColorRole.LinkVisited, QColor(128, 0, 128))

        # Границы и тени
        palette.setColor(QPalette.ColorRole.Dark, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.Mid, QColor(128, 128, 128))
        palette.setColor(QPalette.ColorRole.Light, QColor(200, 200, 200))

        return palette


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.history = []
        self.groups = {}
        self.current_file = None
        self.settings = QSettings("YourCompany", "FileProcessor")
        self.contrast_mode = "normal"  # normal, dark, light
        self.sort_column = 1  # По умолчанию сортировка по дате
        self.sort_order = Qt.SortOrder.DescendingOrder  # По умолчанию по убыванию
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
        self.history_tab = self.create_history_tab()
        central_widget.addTab(self.history_tab, "История обработки")

        # Вкладка групп
        self.groups_tab = self.create_groups_tab()
        central_widget.addTab(self.groups_tab, "Управление группами")

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

    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Группа фильтров и сортировки
        filter_group = QGroupBox("Фильтры, поиск и сортировка")
        filter_layout = QVBoxLayout()

        # Первая строка - фильтры
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Фильтр по группе:"))
        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы")
        self.group_filter.currentTextChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.group_filter)

        filters_layout.addWidget(QLabel("Поиск:"))
        self.search_field = QLineEdit()
        self.search_field.textChanged.connect(self.apply_filters)
        filters_layout.addWidget(self.search_field)
        filter_layout.addLayout(filters_layout)

        # Вторая строка - сортировка
        sort_layout = QHBoxLayout()
        sort_layout.addWidget(QLabel("Сортировка:"))

        self.sort_combo = QComboBox()
        self.sort_combo.addItem("По дате (новые сверху)")
        self.sort_combo.addItem("По дате (старые сверху)")
        self.sort_combo.addItem("По имени файла (А-Я)")
        self.sort_combo.addItem("По имени файла (Я-А)")
        self.sort_combo.addItem("По группе (А-Я)")
        self.sort_combo.addItem("По группе (Я-А)")
        self.sort_combo.currentIndexChanged.connect(self.apply_sorting)
        sort_layout.addWidget(self.sort_combo)

        btn_reset_filters = QPushButton("Сбросить фильтры")
        btn_reset_filters.clicked.connect(self.reset_filters)
        sort_layout.addWidget(btn_reset_filters)

        filter_layout.addLayout(sort_layout)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)

        # Таблица истории
        self.history_table = QTableWidget(0, 4)
        self.history_table.setHorizontalHeaderLabels(["Файл", "Дата", "Результат", "Группа"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Включаем сортировку по клику на заголовок
        self.history_table.setSortingEnabled(True)
        self.history_table.horizontalHeader().sectionClicked.connect(self.header_clicked)

        layout.addWidget(self.history_table)

        # Контекстное меню для таблицы
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_history_context_menu)

        widget.setLayout(layout)
        return widget

    def create_groups_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Список групп
        groups_group = QGroupBox("Группы файлов")
        groups_layout = QVBoxLayout()
        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.show_group_files)
        groups_layout.addWidget(self.groups_list)
        groups_group.setLayout(groups_layout)
        layout.addWidget(groups_group)

        # Файлы в группе
        files_group = QGroupBox("Файлы в выбранной группе")
        files_layout = QVBoxLayout()
        self.group_files_list = QListWidget()
        files_layout.addWidget(self.group_files_list)
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)

        # Управление группами
        manage_group = QGroupBox("Управление группами")
        manage_layout = QHBoxLayout()
        self.new_group_name = QLineEdit()
        self.new_group_name.setPlaceholderText("Название новой группы")
        btn_add_group = QPushButton("Создать группу")
        btn_add_group.clicked.connect(self.create_group)

        btn_remove_group = QPushButton("Удалить группу")
        btn_remove_group.clicked.connect(self.remove_group)

        manage_layout.addWidget(self.new_group_name)
        manage_layout.addWidget(btn_add_group)
        manage_layout.addWidget(btn_remove_group)
        manage_group.setLayout(manage_layout)
        layout.addWidget(manage_group)

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
                'id': len(self.history)  # Уникальный идентификатор
            }
            self.history.append(history_item)
            self.update_history_table()
            self.save_settings()
        else:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите файл")

    def update_history_table(self):
        # Временно отключаем сортировку для обновления данных
        self.history_table.setSortingEnabled(False)

        self.history_table.setRowCount(len(self.history))
        for row, item in enumerate(self.history):
            # Создаем элементы для всех ячеек
            file_item = QTableWidgetItem(item['file'])
            date_item = QTableWidgetItem(item['date'])
            result_item = QTableWidgetItem(item['result'])
            group_item = QTableWidgetItem(item['group'])

            # Сохраняем ID в UserRole для корректной идентификации
            file_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            date_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            result_item.setData(Qt.ItemDataRole.UserRole, item['id'])
            group_item.setData(Qt.ItemDataRole.UserRole, item['id'])

            self.history_table.setItem(row, 0, file_item)
            self.history_table.setItem(row, 1, date_item)
            self.history_table.setItem(row, 2, result_item)
            self.history_table.setItem(row, 3, group_item)

        # Включаем сортировку обратно
        self.history_table.setSortingEnabled(True)

        # Применяем текущую сортировку
        self.apply_current_sorting()

        # Применяем фильтры
        self.apply_filters()

    def apply_filters(self):
        # Применение фильтров к таблице истории
        group_filter = self.group_filter.currentText()
        search_text = self.search_field.text().lower()

        for row in range(self.history_table.rowCount()):
            should_show = True

            # Безопасная проверка фильтра по группе
            if group_filter != "Все группы":
                group_item = self.history_table.item(row, 3)
                if group_item is None or group_item.text() != group_filter:
                    should_show = False

            # Безопасная проверка поискового запроса
            if search_text and should_show:
                file_item = self.history_table.item(row, 0)
                if file_item is None or search_text not in file_item.text().lower():
                    should_show = False

            self.history_table.setRowHidden(row, not should_show)

    def reset_filters(self):
        self.group_filter.setCurrentIndex(0)
        self.search_field.clear()
        self.sort_combo.setCurrentIndex(0)
        self.apply_filters()

    def apply_sorting(self, index):
        # Применяем выбранную сортировку
        if index == 0:  # По дате (новые сверху)
            self.sort_column = 1
            self.sort_order = Qt.SortOrder.DescendingOrder
        elif index == 1:  # По дате (старые сверху)
            self.sort_column = 1
            self.sort_order = Qt.SortOrder.AscendingOrder
        elif index == 2:  # По имени файла (А-Я)
            self.sort_column = 0
            self.sort_order = Qt.SortOrder.AscendingOrder
        elif index == 3:  # По имени файла (Я-А)
            self.sort_column = 0
            self.sort_order = Qt.SortOrder.DescendingOrder
        elif index == 4:  # По группе (А-Я)
            self.sort_column = 3
            self.sort_order = Qt.SortOrder.AscendingOrder
        elif index == 5:  # По группе (Я-А)
            self.sort_column = 3
            self.sort_order = Qt.SortOrder.DescendingOrder

        self.apply_current_sorting()

    def apply_current_sorting(self):
        # Применяем текущую сортировку к таблице
        if self.history_table.rowCount() > 0:
            self.history_table.sortItems(self.sort_column, self.sort_order)

    def header_clicked(self, logical_index):
        # Обработка клика на заголовок таблицы
        if self.history_table.horizontalHeader().sortIndicatorSection() == logical_index:
            # Если кликнули на тот же столбец, меняем порядок сортировки
            current_order = self.history_table.horizontalHeader().sortIndicatorOrder()
            new_order = Qt.SortOrder.DescendingOrder if current_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
            self.history_table.sortItems(logical_index, new_order)

            # Обновляем комбобокс сортировки в соответствии с выбранной сортировкой
            if logical_index == 0:  # Столбец "Файл"
                self.sort_combo.setCurrentIndex(2 if new_order == Qt.SortOrder.AscendingOrder else 3)
            elif logical_index == 1:  # Столбец "Дата"
                self.sort_combo.setCurrentIndex(1 if new_order == Qt.SortOrder.AscendingOrder else 0)
            elif logical_index == 3:  # Столбец "Группа"
                self.sort_combo.setCurrentIndex(4 if new_order == Qt.SortOrder.AscendingOrder else 5)
        else:
            # Если кликнули на другой столбец, сортируем по нему
            self.history_table.sortItems(logical_index, Qt.SortOrder.AscendingOrder)

            # Обновляем комбобокс сортировки в соответствии с выбранной сортировкой
            if logical_index == 0:  # Столбец "Файл"
                self.sort_combo.setCurrentIndex(2)
            elif logical_index == 1:  # Столбец "Дата"
                self.sort_combo.setCurrentIndex(1)
            elif logical_index == 3:  # Столбец "Группа"
                self.sort_combo.setCurrentIndex(4)

    def show_history_context_menu(self, position):
        menu = QMenu()
        add_to_group_action = menu.addAction("Добавить в группу")
        remove_from_group_action = menu.addAction("Удалить из группы")
        action = menu.exec(self.history_table.mapToGlobal(position))

        if action == add_to_group_action:
            self.add_to_group()
        elif action == remove_from_group_action:
            self.remove_from_group()

    def add_to_group(self):
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            # Получаем ID из выбранной строки
            item = self.history_table.item(selected_row, 0)
            if item is not None:
                item_id = item.data(Qt.ItemDataRole.UserRole)

                # Находим запись в истории по ID
                history_item = next((item for item in self.history if item['id'] == item_id), None)

                if history_item:
                    if not self.groups:
                        QMessageBox.information(self, "Информация",
                                                "Сначала создайте группу во вкладке 'Управление группами'")
                        return

                    group_name, ok = QInputDialog.getItem(self, "Добавить в группу",
                                                          "Выберите группу:",
                                                          list(self.groups.keys()), 0, False)
                    if ok and group_name:
                        # Обновляем группу в истории
                        history_item['group'] = group_name

                        # Добавляем ID в группу
                        if item_id not in self.groups[group_name]:
                            self.groups[group_name].append(item_id)

                        self.update_history_table()
                        self.update_group_filters()
                        self.save_settings()

                        # Обновляем список файлов, если эта группа выбрана
                        current_group_item = self.groups_list.currentItem()
                        if current_group_item and current_group_item.text() == group_name:
                            self.show_group_files(current_group_item)

    def remove_from_group(self):
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            # Получаем ID из выбранной строки
            item = self.history_table.item(selected_row, 0)
            if item is not None:
                item_id = item.data(Qt.ItemDataRole.UserRole)

                # Находим запись в истории по ID
                history_item = next((item for item in self.history if item['id'] == item_id), None)

                if history_item and history_item['group'] != 'Без группы':
                    # Удаляем из группы
                    group_name = history_item['group']
                    if item_id in self.groups[group_name]:
                        self.groups[group_name].remove(item_id)

                    # Обновляем историю
                    history_item['group'] = 'Без группы'

                    self.update_history_table()
                    self.save_settings()

                    # Обновляем список файлов, если эта группа выбрана
                    current_group_item = self.groups_list.currentItem()
                    if current_group_item and current_group_item.text() == group_name:
                        self.show_group_files(current_group_item)

    def create_group(self):
        group_name = self.new_group_name.text().strip()
        if group_name:
            if group_name not in self.groups:
                self.groups[group_name] = []
                self.groups_list.addItem(group_name)
                self.update_group_filters()
                self.new_group_name.clear()
                self.save_settings()
                QMessageBox.information(self, "Успех", f"Группа '{group_name}' создана")
            else:
                QMessageBox.warning(self, "Ошибка", "Группа с таким именем уже существует")
        else:
            QMessageBox.warning(self, "Ошибка", "Введите название группы")

    def remove_group(self):
        current_item = self.groups_list.currentItem()
        if current_item:
            group_name = current_item.text()
            reply = QMessageBox.question(self, "Удаление группы",
                                         f"Вы уверены, что хотите удалить группу '{group_name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                # Удаляем группу
                del self.groups[group_name]

                # Обновляем историю - все файлы из этой группы становятся без группы
                for item in self.history:
                    if item['group'] == group_name:
                        item['group'] = 'Без группы'

                # Удаляем группу из списка
                self.groups_list.takeItem(self.groups_list.row(current_item))

                self.update_history_table()
                self.update_group_filters()
                self.save_settings()

                QMessageBox.information(self, "Успех", f"Группа '{group_name}' удалена")
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите группу для удаления")

    def show_group_files(self, item):
        group_name = item.text()
        self.group_files_list.clear()

        # Получаем все ID файлов в группе
        file_ids = self.groups.get(group_name, [])

        # Находим соответствующие записи в истории
        for file_id in file_ids:
            history_item = next((item for item in self.history if item['id'] == file_id), None)
            if history_item:
                self.group_files_list.addItem(f"{history_item['file']} - {history_item['date']}")

    def update_group_filters(self):
        current_text = self.group_filter.currentText()
        self.group_filter.clear()
        self.group_filter.addItem("Все группы")
        self.group_filter.addItems(list(self.groups.keys()))

        # Восстанавливаем предыдущий выбор, если он еще существует
        index = self.group_filter.findText(current_text)
        if index >= 0:
            self.group_filter.setCurrentIndex(index)

    def set_contrast_mode(self, mode):
        self.contrast_mode = mode
        self.apply_styles()
        self.save_settings()

    def apply_styles(self):
        if self.contrast_mode == "dark":
            # Применяем темную высококонтрастную палитру
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
            app.setPalette(app.style().standardPalette())
            app.setStyleSheet("")
            app.setStyle(QStyleFactory.create("Fusion"))

    def save_settings(self):
        self.settings.setValue("contrast_mode", self.contrast_mode)
        self.settings.setValue("history", json.dumps(self.history))
        self.settings.setValue("groups", json.dumps(self.groups))
        self.settings.setValue("sort_column", self.sort_column)
        self.settings.setValue("sort_order", self.sort_order.value)

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

        # Загрузка истории
        history_json = self.settings.value("history", "[]")
        try:
            self.history = json.loads(history_json)
            # Восстанавливаем ID для старых записей, если их нет
            for i, item in enumerate(self.history):
                if 'id' not in item:
                    item['id'] = i
        except:
            self.history = []

        # Загрузка групп
        groups_json = self.settings.value("groups", "{}")
        try:
            self.groups = json.loads(groups_json)
            # Преобразуем ID в int для совместимости
            for group_name in self.groups:
                self.groups[group_name] = [int(id) for id in self.groups[group_name]]
        except:
            self.groups = {}

        # Обновляем интерфейс
        self.groups_list.addItems(self.groups.keys())
        self.update_group_filters()
        self.update_history_table()

        # Загрузка настроек сортировки
        self.sort_column = self.settings.value("sort_column", 1, type=int)
        sort_order_int = self.settings.value("sort_order", Qt.SortOrder.DescendingOrder.value, type=int)
        self.sort_order = Qt.SortOrder(sort_order_int)

        # Устанавливаем соответствующий индекс в комбобоксе сортировки
        if self.sort_column == 1:  # Дата
            self.sort_combo.setCurrentIndex(0 if self.sort_order == Qt.SortOrder.DescendingOrder else 1)
        elif self.sort_column == 0:  # Имя файла
            self.sort_combo.setCurrentIndex(2 if self.sort_order == Qt.SortOrder.AscendingOrder else 3)
        elif self.sort_column == 3:  # Группа
            self.sort_combo.setCurrentIndex(4 if self.sort_order == Qt.SortOrder.AscendingOrder else 5)

        # Применяем стили после загрузки настроек
        self.apply_styles()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())