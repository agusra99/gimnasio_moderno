# views/whatsapp_reminder.py
import sqlite3
import webbrowser
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QSpinBox, QPushButton, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QMessageBox, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt


class WhatsappReminderView(QWidget):
    """Ventana para enviar recordatorios por WhatsApp a socios próximos a vencer."""
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.socios = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # --- Título ---
        title = QLabel("💬 Enviar Recordatorios por WhatsApp")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: #0078D7;
            padding: 10px;
        """)
        layout.addWidget(title)

        # --- Grupo de configuración ---
        group_config = QGroupBox("⚙️ Configuración de aviso")
        config_layout = QHBoxLayout()
        self.spin_dias = QSpinBox()
        self.spin_dias.setRange(1, 30)
        self.spin_dias.setValue(3)
        self.btn_buscar = QPushButton("🔍 Buscar socios")
        self.btn_buscar.clicked.connect(self.buscar_socios)

        config_layout.addWidget(QLabel("Avisar con"))
        config_layout.addWidget(self.spin_dias)
        config_layout.addWidget(QLabel("días antes del vencimiento"))
        config_layout.addStretch()
        config_layout.addWidget(self.btn_buscar)
        group_config.setLayout(config_layout)
        layout.addWidget(group_config)

        # --- Tabla de socios ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["Seleccionar", "Nombre", "Teléfono", "Último Pago", "Días Restantes"])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ccc;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #0078d7;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.tabla)

        # --- Botón enviar ---
        self.btn_enviar = QPushButton("📨 Enviar WhatsApp")
        self.btn_enviar.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #25D366;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background: #1EBE5D; }
        """)
        self.btn_enviar.clicked.connect(self.enviar_mensajes)
        layout.addWidget(self.btn_enviar)

    # === FUNCIONES ===

    def buscar_socios(self):
        """Busca socios a los que se les vence pronto la cuota."""
        dias_aviso = self.spin_dias.value()
        hoy = datetime.now().date()

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("""
            SELECT s.id, s.nombre || ' ' || s.apellido, s.telefono,
                   MAX(p.fecha_pago)
            FROM socios s
            LEFT JOIN pagos p ON s.id = p.socio_id
            WHERE s.activo = 1
            GROUP BY s.id
        """)

        socios = c.fetchall()
        conn.close()

        proximos = []
        for s in socios:
            if not s[3]:
                continue
            fecha_pago = datetime.strptime(s[3], "%Y-%m-%d").date()
            dias_transcurridos = (hoy - fecha_pago).days
            dias_restantes = 30 - dias_transcurridos
            if 0 < dias_restantes <= dias_aviso:
                proximos.append((s[0], s[1], s[2], s[3], dias_restantes))

        self._mostrar_socios(proximos)

    def _mostrar_socios(self, socios):
        """Muestra los socios en la tabla."""
        self.tabla.setRowCount(len(socios))
        for i, s in enumerate(socios):
            chk = QCheckBox()
            self.tabla.setCellWidget(i, 0, chk)
            self.tabla.setItem(i, 1, QTableWidgetItem(s[1]))
            self.tabla.setItem(i, 2, QTableWidgetItem(s[2] or ""))
            self.tabla.setItem(i, 3, QTableWidgetItem(s[3]))
            self.tabla.setItem(i, 4, QTableWidgetItem(str(s[4])))

    def enviar_mensajes(self):
        """Envía mensajes de WhatsApp a los seleccionados."""
        seleccionados = []
        for i in range(self.tabla.rowCount()):
            chk = self.tabla.cellWidget(i, 0)
            if chk and chk.isChecked():
                nombre = self.tabla.item(i, 1).text()
                telefono = self.tabla.item(i, 2).text()
                dias = self.tabla.item(i, 4).text()
                if telefono:
                    seleccionados.append((nombre, telefono, dias))

        if not seleccionados:
            QMessageBox.warning(self, "Atención", "Seleccioná al menos un socio para enviar el mensaje.")
            return

        for s in seleccionados:
            nombre, telefono, dias = s
            mensaje = f"Hola {nombre}, estás a {dias} días de vencer tu cuota del gimnasio. Te esperamos para renovar"
            link = f"https://wa.me/{telefono.replace('+', '').replace(' ', '')}?text={mensaje.replace(' ', '%20')}"
            webbrowser.open(link)

        QMessageBox.information(self, "✅ Listo", f"Se abrieron {len(seleccionados)} chats de WhatsApp en el navegador.")
