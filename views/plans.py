"""
views/plans.py
Vista para la gestión de planes del gimnasio.
Permite crear, editar y eliminar planes.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLineEdit, QSpinBox, QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt


class PlansView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Gestión de Planes")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:600; margin:10px;")
        layout.addWidget(title)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Duración (días)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # Inputs
        form_layout = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre del plan")
        self.input_precio = QDoubleSpinBox()
        self.input_precio.setRange(0, 100000)
        self.input_precio.setPrefix("$")
        self.input_duracion = QSpinBox()
        self.input_duracion.setRange(1, 365)
        self.input_duracion.setSuffix(" días")

        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_precio)
        form_layout.addWidget(self.input_duracion)

        layout.addLayout(form_layout)

        # Botones
        btn_layout = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar")
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_editar = QPushButton("Editar")

        for b in (self.btn_agregar, self.btn_editar, self.btn_eliminar):
            b.setStyleSheet("padding:8px 14px; border-radius:6px; background:#2196F3; color:white;")
            b.setCursor(Qt.PointingHandCursor)

        btn_layout.addWidget(self.btn_agregar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)

        layout.addLayout(btn_layout)
        layout.addStretch()
        self.setLayout(layout)

        # Eventos
        self.btn_agregar.clicked.connect(self.agregar_plan)
        self.btn_eliminar.clicked.connect(self.eliminar_plan)
        self.btn_editar.clicked.connect(self.editar_plan)
        self.table.cellClicked.connect(self.seleccionar_plan)

        self.plan_seleccionado = None
        self.cargar_planes()

    def cargar_planes(self):
        planes = self.controller.obtener_planes()
        self.table.setRowCount(len(planes))
        for row, plan in enumerate(planes):
            for col, valor in enumerate(plan):
                self.table.setItem(row, col, QTableWidgetItem(str(valor)))

    def agregar_plan(self):
        nombre = self.input_nombre.text()
        precio = self.input_precio.value()
        duracion = self.input_duracion.value()

        try:
            self.controller.agregar_plan(nombre, precio, duracion)
            QMessageBox.information(self, "Éxito", "Plan agregado correctamente.")
            self.cargar_planes()
            self.input_nombre.clear()
            self.input_precio.setValue(0)
            self.input_duracion.setValue(1)
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def eliminar_plan(self):
        if not self.plan_seleccionado:
            QMessageBox.warning(self, "Error", "Seleccioná un plan para eliminar.")
            return

        self.controller.eliminar_plan(self.plan_seleccionado)
        QMessageBox.information(self, "Éxito", "Plan eliminado correctamente.")
        self.plan_seleccionado = None
        self.cargar_planes()

    def editar_plan(self):
        if not self.plan_seleccionado:
            QMessageBox.warning(self, "Error", "Seleccioná un plan para editar.")
            return

        nombre = self.input_nombre.text()
        precio = self.input_precio.value()
        duracion = self.input_duracion.value()

        try:
            self.controller.actualizar_plan(self.plan_seleccionado, nombre, precio, duracion)
            QMessageBox.information(self, "Éxito", "Plan actualizado correctamente.")
            self.cargar_planes()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def seleccionar_plan(self, fila, _):
        self.plan_seleccionado = int(self.table.item(fila, 0).text())
        self.input_nombre.setText(self.table.item(fila, 1).text())
        self.input_precio.setValue(float(self.table.item(fila, 2).text()))
        self.input_duracion.setValue(int(self.table.item(fila, 3).text()))
