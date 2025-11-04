import sys
import sqlite3
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QHBoxLayout, QMessageBox, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

DB_PATH = "gimnasio.db"

class VentanaEstadoPagos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estado de Pagos de Socios")
        self.setMinimumWidth(850)
        self.layout = QVBoxLayout(self)

        titulo = QLabel("🧾 Estado de Pagos")
        titulo.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        self.layout.addWidget(titulo)

        # Botón actualizar
        btn_layout = QHBoxLayout()
        self.btn_actualizar = QPushButton("Actualizar")
        self.btn_actualizar.clicked.connect(self.cargar_datos)
        btn_layout.addWidget(self.btn_actualizar)
        self.layout.addLayout(btn_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "Socio", "Teléfono", "Fecha último pago", "Fecha vencimiento", "Días restantes", "Estado"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabla)

        self.cargar_datos()

    def conectar(self):
        return sqlite3.connect(DB_PATH)

    def cargar_datos(self):
        self.tabla.setRowCount(0)
        conn = self.conectar()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    s.nombre, s.apellido, s.telefono, 
                    p.fecha_pago, 
                    DATE(p.fecha_pago, '+' || pl.duracion_dias || ' days') AS fecha_vencimiento
                FROM pagos p
                JOIN socios s ON s.id = p.socio_id
                JOIN planes pl ON pl.id = s.plan_id
                WHERE s.activo = 1
                GROUP BY s.id
                ORDER BY p.fecha_pago DESC
            """)
            registros = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo leer la base:\n{e}")
            conn.close()
            return
        conn.close()

        hoy = datetime.now().date()

        for nombre, apellido, telefono, fecha_pago, fecha_vto_str in registros:
            if not fecha_pago or not fecha_vto_str:
                continue
            fecha_vto = datetime.strptime(fecha_vto_str, "%Y-%m-%d").date()
            dias_restantes = (fecha_vto - hoy).days

            row = self.tabla.rowCount()
            self.tabla.insertRow(row)
            self.tabla.setItem(row, 0, QTableWidgetItem(f"{nombre} {apellido}"))
            self.tabla.setItem(row, 1, QTableWidgetItem(telefono))
            self.tabla.setItem(row, 2, QTableWidgetItem(str(fecha_pago)))
            self.tabla.setItem(row, 3, QTableWidgetItem(str(fecha_vto)))
            self.tabla.setItem(row, 4, QTableWidgetItem(str(dias_restantes)))

            # Estado visual
            if dias_restantes < 0:
                estado = "🔴 Vencido"
                color = QColor(255, 80, 80)
            elif dias_restantes <= 5:
                estado = "🟡 Por vencer"
                color = QColor(255, 220, 80)
            else:
                estado = "🟢 Al día"
                color = QColor(80, 200, 120)

            item_estado = QTableWidgetItem(estado)
            item_estado.setBackground(color)
            self.tabla.setItem(row, 5, item_estado)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaEstadoPagos()
    ventana.show()
    sys.exit(app.exec())
