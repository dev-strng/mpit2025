import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QComboBox, QLineEdit, QPushButton, QGroupBox,
                             QMenu, QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt


class HistoryManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.history = []
        self.sort_column = 1
        self.sort_order = Qt.SortOrder.DescendingOrder

    def create_history_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        filter_group = QGroupBox("Фильтры, поиск и сортировка")
        filter_layout = QVBoxLayout()

        # Первая строка - фильтры
        filters_layout = QHBoxLayout()
        filters_layout.addWidget(QLabel("Фильтр по проекту:"))
        self.group_filter = QComboBox()
        self.group_filter.addItem("Все проекты")
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
        self.sort_combo.addItem("По проекту (А-Я)")
        self.sort_combo.addItem("По проекту (Я-А)")
        self.sort_combo.addItem("По результату (А-Я)")
        self.sort_combo.addItem("По результату (Я-А)")

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
        self.history_table.setHorizontalHeaderLabels(["Файл", "Дата", "Результат", "Проект"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # Включаем сортировку по клику на заголовок
        self.history_table.setSortingEnabled(False)
        self.history_table.horizontalHeader().sectionClicked.connect(self.header_clicked)

        layout.addWidget(self.history_table)

        # Контекстное меню для таблицы
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_history_context_menu)

        widget.setLayout(layout)
        return widget

    def add_to_history(self, file_item):
        self.history.append(file_item)
        self.update_history_table()

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
            if group_filter != "Все проекты":
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
        elif index == 4:  # По результату (А-Я)
            self.sort_column = 2
            self.sort_order = Qt.SortOrder.AscendingOrder
        elif index == 5:  # По результату (Я-А)
            self.sort_column = 2
            self.sort_order = Qt.SortOrder.DescendingOrder
        elif index == 6:  # По проекту (А-Я)
            self.sort_column = 3
            self.sort_order = Qt.SortOrder.AscendingOrder
        elif index == 7:  # По проекту (Я-А)
            self.sort_column = 3
            self.sort_order = Qt.SortOrder.DescendingOrder

        self.apply_current_sorting()

    def apply_current_sorting(self):
        # Применяем текущую сортировку к таблице
        if self.history_table.rowCount() > 0:
            self.history_table.sortItems(self.sort_column, self.sort_order)

    def header_clicked(self, logical_index):
        # Переключение сортировки
        if self.sort_column == logical_index:
            self.sort_order = (
                Qt.SortOrder.AscendingOrder
                if self.sort_order == Qt.SortOrder.DescendingOrder
                else Qt.SortOrder.DescendingOrder
            )
        else:
            self.sort_column = logical_index
            self.sort_order = Qt.SortOrder.AscendingOrder

        self.history_table.sortItems(self.sort_column, self.sort_order)
        self.history_table.horizontalHeader().setSortIndicator(self.sort_column, self.sort_order)

        # Синхронизируем комбобокс
        if logical_index == 0:  # Файл
            self.sort_combo.setCurrentIndex(2 if self.sort_order == Qt.SortOrder.AscendingOrder else 3)
        elif logical_index == 1:  # Дата
            self.sort_combo.setCurrentIndex(1 if self.sort_order == Qt.SortOrder.AscendingOrder else 0)
        elif logical_index == 2:  # Результат
            self.sort_combo.setCurrentIndex(6 if self.sort_order == Qt.SortOrder.AscendingOrder else 7)
        elif logical_index == 3:  # Проект
            self.sort_combo.setCurrentIndex(4 if self.sort_order == Qt.SortOrder.AscendingOrder else 5)

    def show_history_context_menu(self, position):
        menu = QMenu()
        add_to_group_action = menu.addAction("Добавить в проект")
        remove_from_group_action = menu.addAction("Удалить из проекта")
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
                    if not self.main_window.group_manager.groups:
                        QMessageBox.information(self.main_window, "Информация",
                                                "Сначала создайте проект во вкладке 'Управление группами'")
                        return

                    group_name, ok = QInputDialog.getItem(self.main_window, "Добавить в проект",
                                                          "Выберите проект:",
                                                          list(self.main_window.group_manager.groups.keys()), 0, False)
                    if ok and group_name:
                        # Обновляем группу в истории
                        history_item['group'] = group_name

                        # Добавляем ID в группу
                        if item_id not in self.main_window.group_manager.groups[group_name]:
                            self.main_window.group_manager.groups[group_name].append(item_id)

                        self.update_history_table()
                        self.main_window.group_manager.update_group_filters()
                        self.main_window.save_settings()

                        # Обновляем список файлов, если эта группа выбрана
                        current_group_item = self.main_window.group_manager.groups_list.currentItem()
                        if current_group_item and current_group_item.text() == group_name:
                            self.main_window.group_manager.show_group_files(current_group_item)

    def remove_from_group(self):
        selected_row = self.history_table.currentRow()
        if selected_row >= 0:
            # Получаем ID из выбранной строки
            item = self.history_table.item(selected_row, 0)
            if item is not None:
                item_id = item.data(Qt.ItemDataRole.UserRole)

                # Находим запись в истории по ID
                history_item = next((item for item in self.history if item['id'] == item_id), None)

                if history_item and history_item['group'] != 'Черновик':
                    # Удаляем из группы
                    group_name = history_item['group']
                    if item_id in self.main_window.group_manager.groups[group_name]:
                        self.main_window.group_manager.groups[group_name].remove(item_id)

                    # Обновляем историю
                    history_item['group'] = 'Без проекта'

                    self.update_history_table()
                    self.main_window.save_settings()

                    # Обновляем список файлов, если эта группа выбрана
                    current_group_item = self.main_window.group_manager.groups_list.currentItem()
                    if current_group_item and current_group_item.text() == group_name:
                        self.main_window.group_manager.show_group_files(current_group_item)

    def update_group_filters(self):
        current_text = self.group_filter.currentText()
        self.group_filter.clear()
        self.group_filter.addItem("Все проекты")
        self.group_filter.addItems(list(self.main_window.group_manager.groups.keys()))

        # Восстанавливаем предыдущий выбор, если он еще существует
        index = self.group_filter.findText(current_text)
        if index >= 0:
            self.group_filter.setCurrentIndex(index)

    def save_settings(self):
        return {
            'history': self.history,
            'sort_column': self.sort_column,
            'sort_order': self.sort_order.value
        }

    def load_settings(self, settings):
        # Загрузка истории
        history = settings.get('history', [])
        self.history = history

        # Восстанавливаем ID для старых записей, если их нет
        for i, item in enumerate(self.history):
            if 'id' not in item:
                item['id'] = i

        # Загрузка настроек сортировки
        self.sort_column = settings.get('sort_column', 1)
        sort_order_int = settings.get('sort_order', Qt.SortOrder.DescendingOrder.value)
        self.sort_order = Qt.SortOrder(sort_order_int)

        # Устанавливаем соответствующий индекс в комбобоксе сортировки
        if self.sort_column == 1:  # Дата
            self.sort_combo.setCurrentIndex(0 if self.sort_order == Qt.SortOrder.DescendingOrder else 1)
        elif self.sort_column == 0:  # Имя файла
            self.sort_combo.setCurrentIndex(2 if self.sort_order == Qt.SortOrder.AscendingOrder else 3)
        elif self.sort_column == 3:  # Проекты
            self.sort_combo.setCurrentIndex(4 if self.sort_order == Qt.SortOrder.AscendingOrder else 5)