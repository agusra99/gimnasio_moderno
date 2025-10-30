"""
views/alerts.py
Vista para mostrar alertas y notificaciones de socios con pagos atrasados.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt


class AlertsView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Alertas de Pagos")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:600; margin:10px;")
        layout.addWidget(title)

        # Tabla de alertas
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Socio", "Mensaje", "Fecha"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Botón para marcar como leída
        btn_layout = QHBoxLayout()
        self.btn_marcar_leida = QPushButton("Marcar como Leída")
        self.btn_marcar_leida.setStyleSheet("padding:8px 16px; border-radius:6px; background:#FF9800; color:white;")
        btn_layout.addWidget(self.btn_marcar_leida)
        layout.addLayout(btn_layout)

        layout.addStretch()
        self.setLayout(layout)

        # Conexiones
        self.btn_marcar_leida.clicked.connect(self.marcar_como_leida)

        self.cargar_alertas()

    def cargar_alertas(self):
        alertas = self.controller.obtener_alertas_no_leidas()
        self.table.setRowCount(len(alertas))

        for row, alerta in enumerate(alertas):
            self.table.setItem(row, 0, QTableWidgetItem(str(alerta[0])))
            self.table.setItem(row, 1, QTableWidgetItem(alerta[1]))
            self.table.setItem(row, 2, QTableWidgetItem(alerta[2]))
            self.table.setItem(row, 3, QTableWidgetItem(alerta[3]))

    def marcar_como_leida(self):
        fila = self.table.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná una alerta para marcar como leída.")
            return

        alerta_id = int(self.table.item(fila, 0).text())
        self.controller.marcar_alerta_leida(alerta_id)
        QMessageBox.information(self, "Éxito", "Alerta marcada como leída.")
        self.cargar_alertas()