import json
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QListWidget, QListWidgetItem, QLineEdit,
                             QPushButton, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt


class GroupManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.groups = {}

    def create_groups_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        groups_group = QGroupBox("Файлы проектов")
        groups_layout = QVBoxLayout()
        self.groups_list = QListWidget()
        self.groups_list.itemClicked.connect(self.show_group_files)
        groups_layout.addWidget(self.groups_list)
        groups_group.setLayout(groups_layout)
        layout.addWidget(groups_group)

        # Файлы в группе
        files_group = QGroupBox("Файлы в выбранном проекте")
        files_layout = QVBoxLayout()
        self.group_files_list = QListWidget()
        files_layout.addWidget(self.group_files_list)
        files_group.setLayout(files_layout)
        layout.addWidget(files_group)

        # Управление группами
        manage_group = QGroupBox("Управление проектами")
        manage_layout = QHBoxLayout()
        self.new_group_name = QLineEdit()
        self.new_group_name.setPlaceholderText("Название нового проекта")
        btn_add_group = QPushButton("Создать проект")
        btn_add_group.clicked.connect(self.create_group)

        btn_remove_group = QPushButton("Удалить проект")
        btn_remove_group.clicked.connect(self.remove_group)

        manage_layout.addWidget(self.new_group_name)
        manage_layout.addWidget(btn_add_group)
        manage_layout.addWidget(btn_remove_group)
        manage_group.setLayout(manage_layout)
        layout.addWidget(manage_group)

        widget.setLayout(layout)
        return widget

    def create_group(self):
        group_name = self.new_group_name.text().strip()
        if group_name:
            if group_name not in self.groups:
                self.groups[group_name] = []
                self.groups_list.addItem(group_name)
                self.main_window.history_manager.update_group_filters()
                self.new_group_name.clear()
                self.main_window.save_settings()
                QMessageBox.information(self.main_window, "Успех", f"проект '{group_name}' создан")
            else:
                QMessageBox.warning(self.main_window, "Ошибка", "Проект с таким именем уже существует")
        else:
            QMessageBox.warning(self.main_window, "Ошибка", "Введите название проекта")

    def remove_group(self):
        current_item = self.groups_list.currentItem()
        if current_item:
            group_name = current_item.text()
            reply = QMessageBox.question(self.main_window, "Удаление проекта",
                                         f"Вы уверены, что хотите удалить проект '{group_name}'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                # Удаляем группу
                del self.groups[group_name]

                # Обновляем историю - все файлы из этой группы становятся без группы
                for item in self.main_window.history_manager.history:
                    if item['group'] == group_name:
                        item['group'] = 'Без проекта'

                # Удаляем группу из списка
                self.groups_list.takeItem(self.groups_list.row(current_item))

                self.main_window.history_manager.update_history_table()
                self.main_window.history_manager.update_group_filters()
                self.main_window.save_settings()

                QMessageBox.information(self.main_window, "Успех", f"Проект '{group_name}' удалена")
        else:
            QMessageBox.warning(self.main_window, "Ошибка", "Выберите проект для удаления")

    def show_group_files(self, item):
        group_name = item.text()
        self.group_files_list.clear()

        # Получаем все ID файлов в группе
        file_ids = self.groups.get(group_name, [])

        # Находим соответствующие записи в истории
        for file_id in file_ids:
            history_item = next((item for item in self.main_window.history_manager.history if item['id'] == file_id),
                                None)
            if history_item:
                self.group_files_list.addItem(f"{history_item['file']} - {history_item['date']}")

    def update_group_filters(self):
        self.main_window.history_manager.update_group_filters()

    def save_settings(self):
        return {
            'groups': self.groups
        }

    def load_settings(self, settings):
        # Загрузка групп
        groups = settings.get('groups', {})
        self.groups = groups

        # Преобразуем ID в int для совместимости
        for group_name in self.groups:
            self.groups[group_name] = [int(id) for id in self.groups[group_name]]

        # Обновляем интерфейс
        self.groups_list.addItems(self.groups.keys())