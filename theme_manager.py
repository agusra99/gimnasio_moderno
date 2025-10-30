'''"""
theme_manager.py
Gestor de temas claro y oscuro para toda la aplicación.
"""


class ThemeManager:
    """Administra los temas de la aplicación."""
    
    LIGHT_THEME = """
        /* Tema Claro */
        QMainWindow, QWidget {
            background-color: #f4f4f4;
            color: #333;
        }
        
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #005fa3;
        }
        
        QPushButton:pressed {
            background-color: #004578;
        }
        
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 6px;
            background-color: white;
            color: #333;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border-color: #0078d7;
        }
        
        QTableWidget {
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: white;
            alternate-background-color: #f9f9f9;
        }
        
        QHeaderView::section {
            background-color: #0078d7;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: none;
        }
        
        QTableWidget::item:selected {
            background-color: #cce5ff;
            color: black;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #0078d7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #0078d7;
        }
        
        QLabel {
            color: #333;
        }
        
        QFrame {
            background-color: #e8e8e8;
        }
    """
    
    DARK_THEME = """
        /* Tema Oscuro */
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
        }
        
        QPushButton:hover {
            background-color: #1e88e5;
        }
        
        QPushButton:pressed {
            background-color: #1565c0;
        }
        
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 8px;
            border: 2px solid #3a3a3a;
            border-radius: 6px;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border-color: #0078d7;
        }
        
        QComboBox::drop-down {
            border: none;
        }
        
        QComboBox::down-arrow {
            image: none;
            border: none;
        }
        
        QTableWidget {
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            background-color: #2d2d2d;
            alternate-background-color: #252525;
            color: #e0e0e0;
        }
        
        QHeaderView::section {
            background-color: #0078d7;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: none;
        }
        
        QTableWidget::item {
            color: #e0e0e0;
        }
        
        QTableWidget::item:selected {
            background-color: #1e5a8a;
            color: white;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #0078d7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #0078d7;
        }
        
        QLabel {
            color: #e0e0e0;
        }
        
        QFrame {
            background-color: #2d2d2d;
        }
        
        QScrollBar:vertical {
            background-color: #2d2d2d;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #555;
            border-radius: 6px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #666;
        }
        
        QScrollBar:horizontal {
            background-color: #2d2d2d;
            height: 12px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #555;
            border-radius: 6px;
            min-width: 20px;
        }
        /* Hacer transparentes los groupboxes específicos para que el fondo del contenedor oscuro se vea
           y el texto en color claro del tema sea legible */
        QGroupBox#alertasGroup, QGroupBox#proximosGroup {
            background-color: transparent;
            border-color: #F44336; /* conservar bordes visibles si aplica */
            color: #e0e0e0;
        }

        /* Tablas dentro de esos groupboxes deben ser transparentes también */
        QGroupBox#alertasGroup QTableWidget, QGroupBox#proximosGroup QTableWidget {
            background-color: transparent;
            alternate-background-color: transparent;
            gridline-color: rgba(255,255,255,0.06);
            color: #e0e0e0;
        }
    """
    
    def __init__(self):
        self.current_theme = "light"
    
    def get_theme(self):
        """Retorna el tema actual."""
        return self.LIGHT_THEME if self.current_theme == "light" else self.DARK_THEME
    
    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        return self.get_theme()
    
    def is_dark(self):
        """Verifica si el tema actual es oscuro."""
        return self.current_theme == "dark"'''
"""
theme_manager.py
Gestor de temas claro y oscuro para toda la aplicación.
"""

import json
import os


class ThemeManager:
    """Administra los temas de la aplicación con guardado automático."""
    
    CONFIG_FILE = "config_tema.json"

    LIGHT_THEME = """
        /* Tema Claro */
        QMainWindow, QWidget {
            background-color: #f4f4f4;
            color: #333;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
        }
        QPushButton:hover { background-color: #005fa3; }
        QPushButton:pressed { background-color: #004578; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 6px;
            background-color: white;
            color: #333;
        }
        QLineEdit:focus, QComboBox:focus { border-color: #0078d7; }
        QTableWidget {
            border: 1px solid #ddd;
            border-radius: 6px;
            background-color: white;
            alternate-background-color: #f9f9f9;
        }
        QHeaderView::section {
            background-color: #0078d7;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: none;
        }
        QTableWidget::item:selected {
            background-color: #cce5ff;
            color: black;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #0078d7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #0078d7;
        }
        QLabel { color: #333; }
        QFrame { background-color: #e8e8e8; }
    """

    DARK_THEME = """
        /* Tema Oscuro */
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        QPushButton {
            background-color: #0078d7;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-size: 14px;
        }
        QPushButton:hover { background-color: #1e88e5; }
        QPushButton:pressed { background-color: #1565c0; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            padding: 8px;
            border: 2px solid #3a3a3a;
            border-radius: 6px;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QLineEdit:focus, QComboBox:focus { border-color: #0078d7; }
        QTableWidget {
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            background-color: #2d2d2d;
            alternate-background-color: #252525;
            color: #e0e0e0;
        }
        QHeaderView::section {
            background-color: #0078d7;
            color: white;
            padding: 8px;
            font-weight: bold;
            border: none;
        }
        QTableWidget::item:selected {
            background-color: #1e5a8a;
            color: white;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #0078d7;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            padding: 0 5px;
            color: #0078d7;
        }
        QLabel { color: #e0e0e0; }
        QFrame { background-color: #2d2d2d; }
    """

    def __init__(self):
        self.current_theme = self.load_theme()

    def load_theme(self):
        """Carga el tema guardado (light/dark) desde el archivo."""
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("theme", "light")
            except Exception:
                pass
        return "light"

    def save_theme(self):
        """Guarda el tema actual en un archivo JSON."""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump({"theme": self.current_theme}, f)
        except Exception as e:
            print(f"No se pudo guardar el tema: {e}")

    def get_theme(self):
        """Retorna el tema actual."""
        return self.LIGHT_THEME if self.current_theme == "light" else self.DARK_THEME

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro y lo guarda."""
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.save_theme()
        return self.get_theme()

    def is_dark(self):
        """Verifica si el tema actual es oscuro."""
        return self.current_theme == "dark"
