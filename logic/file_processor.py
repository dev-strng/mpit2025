import os
from datetime import datetime

class FileProcessor:
    @staticmethod
    def process_file(filepath):
        # Заглушка для обработки файла
        # В реальном приложении здесь будет ваша логика обработки
        return f"Обработан {os.path.basename(filepath)} ({datetime.now().strftime('%H:%M:%S')})"