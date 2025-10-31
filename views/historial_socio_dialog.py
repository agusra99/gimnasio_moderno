# views/historial_socio_dialog.py
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QFrame, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class HistorialSocioDialog(QDialog):
    """Diálogo para ver el historial completo de pagos de un socio."""
    
    def __init__(self, controller, socio_id, socio_nombre, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.socio_id = socio_id
        self.socio_nombre = socio_nombre
        self.setWindowTitle(f"Historial de Pagos - {socio_nombre}")
        self.setMinimumSize(950, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # --- Encabezado ---
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2196F3, stop:1 #1976D2);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title = QLabel("📜 Historial Completo de Pagos")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        title.setAlignment(Qt.AlignCenter)
        
        nombre_label = QLabel(self.socio_nombre)
        nombre_label.setStyleSheet("font-size: 16px; color: white; margin-top: 5px;")
        nombre_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title)
        title_layout.addWidget(nombre_label)
        layout.addWidget(title_frame)

        # --- Tabla ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha de Pago", "Monto", "Mes Correspondiente", "Método", "Observaciones"
        ])
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 2px solid #2196F3;
                border-radius: 8px;
                background-color: transparent;
                gridline-color: #e0e0e0;
            }
            QHeaderView::section {
                background-color: #2196F3;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #bbdefb;
                color: black;
            }
        """)

        pagos = self.controller.obtener_pagos_socio(self.socio_id)
        self.tabla.setRowCount(len(pagos) if pagos else 1)

        total_pagado = 0
        if not pagos:
            msg = QTableWidgetItem("No hay pagos registrados para este socio")
            msg.setForeground(QColor(150, 150, 150))
            msg.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(0, 0, msg)
            self.tabla.setSpan(0, 0, 1, 5)
        else:
            for row, pago in enumerate(pagos):
                # Fecha
                fecha = QTableWidgetItem(pago[2])
                fecha.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, 0, fecha)

                # Monto
                monto = float(pago[1])
                total_pagado += monto
                item_monto = QTableWidgetItem(f"${monto:,.0f}")
                item_monto.setForeground(QColor(76, 175, 80))
                item_monto.setTextAlignment(Qt.AlignCenter)
                item_monto.setFont(QFont("Arial", 11, QFont.Bold))
                self.tabla.setItem(row, 1, item_monto)

                # Mes
                mes_item = QTableWidgetItem(pago[3])
                mes_item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, 2, mes_item)

                # Método
                metodo = pago[4].capitalize() if pago[4] else "Efectivo"
                metodo_item = QTableWidgetItem(metodo)
                metodo_item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, 3, metodo_item)

                # Observaciones
                obs_item = QTableWidgetItem(pago[5] if pago[5] else "-")
                obs_item.setTextAlignment(Qt.AlignCenter)
                self.tabla.setItem(row, 4, obs_item)

        self.tabla.verticalHeader().setDefaultSectionSize(40)
        self.tabla.resizeColumnsToContents()
        self.tabla.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.tabla)

        # --- Resumen ---
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)

        def crear_card(titulo, valor, color):
            frame = QFrame()
            frame.setStyleSheet(f"QFrame {{ border-left: 5px solid {color}; border-radius: 8px; padding: 15px; }}")
            fl = QVBoxLayout(frame)
            lbl_titulo = QLabel(titulo)
            lbl_titulo.setStyleSheet("font-size: 12px; color: #666;")
            lbl_titulo.setAlignment(Qt.AlignCenter)
            lbl_valor = QLabel(valor)
            lbl_valor.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {color};")
            lbl_valor.setAlignment(Qt.AlignCenter)
            fl.addWidget(lbl_titulo)
            fl.addWidget(lbl_valor)
            return frame

        cantidad = len(pagos)
        promedio = (total_pagado / cantidad) if cantidad > 0 else 0

        stats_layout.addWidget(crear_card("💰 Total Pagado", f"${total_pagado:,.0f}", "#4CAF50"))
        stats_layout.addWidget(crear_card("📊 Cantidad de Pagos", str(cantidad), "#2196F3"))
        stats_layout.addWidget(crear_card("📈 Promedio por Pago", f"${promedio:,.0f}", "#FF9800"))

        layout.addWidget(stats_frame)

        # --- Botón cerrar ---
        btn_cerrar = QPushButton("✓ Cerrar")
        btn_cerrar.setMinimumSize(150, 45)
        btn_cerrar.clicked.connect(self.accept)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                padding: 12px 30px;
                background: #2196F3;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background: #1976D2; }
            QPushButton:pressed { background: #0D47A1; }
        """)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(btn_cerrar)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.setLayout(layout)
