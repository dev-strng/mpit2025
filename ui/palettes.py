from PyQt6.QtGui import QPalette, QColor


class HighContrastDarkPalette:
    @staticmethod
    def get_palette():
        palette = QPalette()
        # Темная высококонтрастная схема
        palette.setColor(QPalette.ColorRole.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 0))
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

        return palette


class HighContrastLightPalette:
    @staticmethod
    def get_palette():
        palette = QPalette()
        # Светлая высококонтрастная схема
        palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
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

        return palette