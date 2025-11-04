import sys
import sqlite3
import webbrowser
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QSpinBox
)
from PySide6.QtCore import Qt

DB_PATH = "gimnasio.db"

class VentanaWhatsApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enviar mensajes por WhatsApp")
        self.setMinimumWidth(800)
        self.layout = QVBoxLayout(self)
        
        # --- Filtro ---
        filtro_layout = QHBoxLayout()
        filtro_layout.addWidget(QLabel("Días antes del vencimiento:"))
        self.dias_spin = QSpinBox()
        self.dias_spin.setRange(1, 30)
        self.dias_spin.setValue(5)
        filtro_layout.addWidget(self.dias_spin)

        self.btn_filtrar = QPushButton("Buscar")
        self.btn_filtrar.clicked.connect(self.cargar_socios)
        filtro_layout.addWidget(self.btn_filtrar)

        self.layout.addLayout(filtro_layout)

        # --- Tabla ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Nombre", "Teléfono", "Fecha Vto", "Días restantes", "Enviar"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.tabla)

        # --- Botón Enviar a todos ---
        btn_layout = QHBoxLayout()
        self.btn_enviar_todos = QPushButton("Enviar a todos")
        self.btn_enviar_todos.clicked.connect(self.enviar_a_todos)
        btn_layout.addWidget(self.btn_enviar_todos)
        self.layout.addLayout(btn_layout)

        self.cargar_socios()

    def conectar(self):
        return sqlite3.connect(DB_PATH)

    def cargar_socios(self):
        """Carga socios cuya cuota vence dentro de los próximos X días"""
        self.tabla.setRowCount(0)
        dias_filtro = self.dias_spin.value()
        hoy = datetime.now().date()

        conn = self.conectar()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT nombre, apellido, telefono, fecha_vencimiento
                FROM vista_vencimientos
                WHERE telefono IS NOT NULL
            """)
            socios = cur.fetchall()
        except Exception as e:
            QMessageBox.critical(self, "Error BD", f"No se pudo leer la base:\n{e}")
            conn.close()
            return
        conn.close()

        for nombre, apellido, telefono, fecha_vto_str in socios:
            if not telefono or not fecha_vto_str:
                continue
            fecha_vto = datetime.strptime(fecha_vto_str, "%Y-%m-%d").date()
            dias_restantes = (fecha_vto - hoy).days
            if 0 <= dias_restantes <= dias_filtro:
                self.agregar_fila(nombre, apellido, telefono, fecha_vto, dias_restantes)

    def agregar_fila(self, nombre, apellido, telefono, fecha_vto, dias_restantes):
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        self.tabla.setItem(row, 0, QTableWidgetItem(f"{nombre} {apellido}"))
        self.tabla.setItem(row, 1, QTableWidgetItem(telefono))
        self.tabla.setItem(row, 2, QTableWidgetItem(str(fecha_vto)))
        self.tabla.setItem(row, 3, QTableWidgetItem(str(dias_restantes)))

        btn = QPushButton("Enviar")
        btn.clicked.connect(lambda: self.enviar_mensaje(nombre, telefono, dias_restantes))
        self.tabla.setCellWidget(row, 4, btn)

    def enviar_mensaje(self, nombre, telefono, dias_restantes):
        """Abre chat de WhatsApp con mensaje personalizado"""
        telefono = telefono.strip().replace(" ", "").replace("-", "")
        if not telefono.startswith("549"):
            telefono = "549" + telefono[-10:]  # Normaliza número argentino

        mensaje = (
            f"Hola {nombre}, tu cuota vence en {dias_restantes} días. "
            f"Podés abonar en recepción para mantener tu membresía activa. ¡Gracias!"
        )
        url = f"https://wa.me/{telefono}?text={mensaje.replace(' ', '%20')}"
        webbrowser.open(url)

    def enviar_a_todos(self):
        filas = self.tabla.rowCount()
        if filas == 0:
            QMessageBox.information(self, "Sin resultados", "No hay socios para enviar mensajes.")
            return

        for i in range(filas):
            nombre = self.tabla.item(i, 0).text()
            telefono = self.tabla.item(i, 1).text()
            dias = int(self.tabla.item(i, 3).text())
            self.enviar_mensaje(nombre, telefono, dias)

        QMessageBox.information(self, "Envío completo", "Se abrieron los chats de WhatsApp para todos los socios.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaWhatsApp()
    ventana.show()
    sys.exit(app.exec())
