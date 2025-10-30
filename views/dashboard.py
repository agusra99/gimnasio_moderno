'''"""
views/dashboard.py
Vista principal (Dashboard) del sistema del gimnasio.
Muestra un resumen general: cantidad de socios, pagos y alertas activas.
Interfaz moderna, minimalista e intuitiva con PySide6.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame
from PySide6.QtCore import Qt


class DashboardView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Panel Principal")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:600; margin:10px;")
        layout.addWidget(title)

        summary_layout = QHBoxLayout()

        self.lbl_socios = self._create_card("Socios activos", "0")
        self.lbl_pagos = self._create_card("Pagos registrados", "0")
        self.lbl_alertas = self._create_card("Alertas pendientes", "0")

        summary_layout.addWidget(self.lbl_socios)
        summary_layout.addWidget(self.lbl_pagos)
        summary_layout.addWidget(self.lbl_alertas)

        layout.addLayout(summary_layout)
        layout.addStretch()

        self.setLayout(layout)

        # Actualiza datos
        self.actualizar_datos()

    def _create_card(self, title, value):
        frame = QFrame()
        frame.setStyleSheet("background:#f9f9f9; border-radius:12px; padding:20px; border:1px solid #eee;")
        box = QVBoxLayout()

        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-size:16px; font-weight:500;")

        lbl_value = QLabel(value)
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setStyleSheet("font-size:28px; font-weight:700; color:#333;")

        box.addWidget(lbl_title)
        box.addWidget(lbl_value)
        frame.setLayout(box)

        frame.value_label = lbl_value  # Para actualización dinámica
        return frame

    def actualizar_datos(self):
        socios = self.controller.obtener_socios()
        pagos = self.controller.pagos.obtener_pagos()
        alertas = self.controller.obtener_alertas_no_leidas()

        self.lbl_socios.value_label.setText(str(len(socios)))
        self.lbl_pagos.value_label.setText(str(len(pagos)))
        self.lbl_alertas.value_label.setText(str(len(alertas)))
'''
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import sqlite3


class DashboardView(QWidget):
    def __init__(self, db_path="gym.db"):
        super().__init__()
        self.db_path = db_path
        self.init_ui()
        self.actualizar_datos()

    def init_ui(self):
        # Layout principal
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("Panel Principal")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet("color: #222; margin-bottom: 10px;")
        layout.addWidget(title)

        # === Tarjetas de resumen ===
        self.frame_container = QWidget()
        self.cards_layout = QGridLayout(self.frame_container)
        self.cards_layout.setSpacing(20)

        self.card_socios = self.create_card("Total de Socios", "0", "#0078d7")
        self.card_pagos = self.create_card("Pagos del Mes", "$0", "#28a745")
        self.card_alertas = self.create_card("Socios con Deuda", "0", "#dc3545")

        self.cards_layout.addWidget(self.card_socios, 0, 0)
        self.cards_layout.addWidget(self.card_pagos, 0, 1)
        self.cards_layout.addWidget(self.card_alertas, 0, 2)

        layout.addWidget(self.frame_container)
        layout.addStretch()

        # Aplicar estilo general
        self.setStyleSheet("""
            QWidget {
                background-color: #f4f6f9;
                color: #333;
                font-family: 'Segoe UI', sans-serif;
            }
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #ddd;
            }
            QLabel {
                font-size: 14px;
            }
        """)

        self.setLayout(layout)

    def create_card(self, title_text, value_text, color):
        """Crea una tarjeta informativa con título y valor."""
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(20, 20, 20, 20)
        frame_layout.setSpacing(10)

        lbl_title = QLabel(title_text)
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 16px;")

        lbl_value = QLabel(value_text)
        lbl_value.setAlignment(Qt.AlignCenter)
        lbl_value.setFont(QFont("Segoe UI", 28, QFont.Bold))
        lbl_value.setStyleSheet("color: #222;")
        lbl_value.setWordWrap(True)
        lbl_value.setMinimumWidth(150)
        lbl_value.setMaximumHeight(60)

        frame_layout.addWidget(lbl_title)
        frame_layout.addWidget(lbl_value)

        frame.lbl_value = lbl_value  # para actualizar después
        return frame

    def actualizar_datos(self):
        """Carga los valores desde la base de datos."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Total de socios
            c.execute("SELECT COUNT(*) FROM socios")
            total_socios = c.fetchone()[0] or 0
            self.card_socios.lbl_value.setText(str(total_socios))

            # Pagos del mes
            c.execute("""
                SELECT COALESCE(SUM(monto), 0)
                FROM pagos
                WHERE strftime('%m', fecha_pago) = strftime('%m', 'now')
            """)
            total_pagos = c.fetchone()[0] or 0
            self.card_pagos.lbl_value.setText(f"${total_pagos:,.0f}".replace(",", "."))

            # Socios con deuda
            c.execute("SELECT COUNT(*) FROM socios WHERE id IN (SELECT socio_id FROM deudas)")
            total_deuda = c.fetchone()[0] or 0
            self.card_alertas.lbl_value.setText(str(total_deuda))

            conn.close()

        except Exception as e:
            print("Error al cargar datos del dashboard:", e)
