'''from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, QDate
import datetime

class MembersView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Gestión de Socios")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Campos de entrada
        form_layout = QHBoxLayout()
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")

        self.input_apellido = QLineEdit()
        self.input_apellido.setPlaceholderText("Apellido")

        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("Teléfono")

        # Combo box de planes
        self.combo_plan = QComboBox()
        self.cargar_planes()

        self.btn_agregar = QPushButton("Agregar Socio")
        self.btn_agregar.clicked.connect(self.agregar_socio)

        form_layout.addWidget(self.input_nombre)
        form_layout.addWidget(self.input_apellido)
        form_layout.addWidget(self.input_telefono)
        form_layout.addWidget(self.combo_plan)
        form_layout.addWidget(self.btn_agregar)
        layout.addLayout(form_layout)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Teléfono", "Plan"])
        layout.addWidget(self.tabla)

        self.setLayout(layout)
        self.cargar_socios()

    def cargar_planes(self):
        """Llena el combo con los planes disponibles."""
        self.combo_plan.clear()
        planes = self.controller.obtener_planes()
        for plan in planes:
            self.combo_plan.addItem(plan[1], plan[0])

    def cargar_socios(self):
        socios = self.controller.obtener_todos()
        self.tabla.setRowCount(len(socios))
        for row, socio in enumerate(socios):
            for col, dato in enumerate(socio[:5]):  # ID, nombre, apellido, teléfono, plan
                item = QTableWidgetItem(str(dato) if dato else "")
                self.tabla.setItem(row, col, item)

    def agregar_socio(self):
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        telefono = self.input_telefono.text().strip()
        plan_id = self.combo_plan.currentData()
        fecha_alta = datetime.date.today().isoformat()

        if not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios.")
            return

        self.controller.agregar(nombre, apellido, telefono, fecha_alta, plan_id)
        self.cargar_socios()
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_telefono.clear()
        QMessageBox.information(self, "Éxito", "Socio agregado correctamente.")
'''
"""
views/members.py
Vista para gestionar socios con búsqueda y filtros mejorados.
"""
"""
views/members.py
Vista para gestionar socios con búsqueda y filtros mejorados.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt
import datetime


class MembersView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gestión de Socios")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # --- BARRA DE BÚSQUEDA ---
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nombre, apellido o teléfono...")
        self.search_input.textChanged.connect(self.buscar_socios)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0078d7;
            }
        """)
        
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_busqueda)
        btn_limpiar.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #6c757d;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #5a6268;
            }
        """)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_limpiar)
        layout.addLayout(search_layout)

        # --- FORMULARIO DE ALTA ---
        form_layout = QHBoxLayout()
        
        self.input_nombre = QLineEdit()
        self.input_nombre.setPlaceholderText("Nombre")
        
        self.input_apellido = QLineEdit()
        self.input_apellido.setPlaceholderText("Apellido")
        
        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("Teléfono")
        
        # Combo box de planes
        self.combo_plan = QComboBox()
        self.cargar_planes()
        
        self.btn_agregar = QPushButton("➕ Agregar Socio")
        self.btn_agregar.clicked.connect(self.agregar_socio)
        self.btn_agregar.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #28a745;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        
        for widget in [self.input_nombre, self.input_apellido, 
                       self.input_telefono, self.combo_plan, self.btn_agregar]:
            form_layout.addWidget(widget)
        
        layout.addLayout(form_layout)

        # --- TABLA DE SOCIOS ---
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Nombre", "Apellido", "Teléfono", "Plan", "Fecha Alta"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
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
        """)
        layout.addWidget(self.tabla)

        # --- BOTONES DE ACCIÓN ---
        btn_layout = QHBoxLayout()
        
        self.btn_editar = QPushButton("✏️ Editar")
        self.btn_editar.clicked.connect(self.editar_socio)
        self.btn_editar.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #ffc107;
                color: #333;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        
        self.btn_eliminar = QPushButton("🗑️ Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar_socio)
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #dc3545;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.cargar_socios()

    def cargar_planes(self):
        """Llena el combo con los planes disponibles."""
        self.combo_plan.clear()
        planes = self.controller.obtener_planes()
        for plan in planes:
            self.combo_plan.addItem(plan[1], plan[0])  # nombre, id

    def cargar_socios(self, filtro=""):
        """Carga socios en la tabla con filtro opcional."""
        socios = self.controller.obtener_todos()
        
        # Aplicar filtro si existe
        if filtro:
            filtro = filtro.lower()
            socios = [s for s in socios if 
                     filtro in str(s[1]).lower() or  # nombre
                     filtro in str(s[2]).lower() or  # apellido
                     filtro in str(s[3]).lower()]    # teléfono
        
        self.tabla.setRowCount(len(socios))
        for row, socio in enumerate(socios):
            self.tabla.setItem(row, 0, QTableWidgetItem(str(socio[0])))  # ID
            self.tabla.setItem(row, 1, QTableWidgetItem(str(socio[1])))  # Nombre
            self.tabla.setItem(row, 2, QTableWidgetItem(str(socio[2])))  # Apellido
            self.tabla.setItem(row, 3, QTableWidgetItem(str(socio[3]) if socio[3] else ""))  # Teléfono
            self.tabla.setItem(row, 5, QTableWidgetItem(str(socio[4]) if socio[4] else ""))  # Fecha
            # Plan (índice 5 en la consulta)
            self.tabla.setItem(row, 4, QTableWidgetItem(str(socio[5]) if socio[5] else "Sin plan"))

    def buscar_socios(self):
        """Busca socios mientras el usuario escribe."""
        filtro = self.search_input.text().strip()
        self.cargar_socios(filtro)

    def limpiar_busqueda(self):
        """Limpia la búsqueda y recarga todos los socios."""
        self.search_input.clear()
        self.cargar_socios()

    def agregar_socio(self):
        """Agrega un nuevo socio."""
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        telefono = self.input_telefono.text().strip()
        plan_id = self.combo_plan.currentData()
        fecha_alta = datetime.date.today().isoformat()

        if not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios.")
            return

        self.controller.agregar(nombre, apellido, telefono, fecha_alta, plan_id)
        self.cargar_socios()
        
        # Limpiar campos
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_telefono.clear()
        
        QMessageBox.information(self, "Éxito", "Socio agregado correctamente.")

    def editar_socio(self):
        """Edita el socio seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un socio para editar.")
            return
        
        # Cargar datos en los campos
        socio_id = int(self.tabla.item(fila, 0).text())
        self.input_nombre.setText(self.tabla.item(fila, 1).text())
        self.input_apellido.setText(self.tabla.item(fila, 2).text())
        self.input_telefono.setText(self.tabla.item(fila, 3).text())
        
        QMessageBox.information(
            self, 
            "Editar", 
            "Modificá los datos y presioná 'Actualizar Socio'"
        )
        
        # Cambiar botón agregar por actualizar
        self.btn_agregar.setText("💾 Actualizar Socio")
        self.btn_agregar.clicked.disconnect()
        self.btn_agregar.clicked.connect(lambda: self.actualizar_socio(socio_id))

    def actualizar_socio(self, socio_id):
        """Actualiza los datos del socio."""
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        telefono = self.input_telefono.text().strip()
        plan_id = self.combo_plan.currentData()

        if not nombre or not apellido:
            QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios.")
            return

        self.controller.actualizar(socio_id, nombre, apellido, telefono, plan_id)
        self.cargar_socios()
        
        # Restaurar botón
        self.btn_agregar.setText("➕ Agregar Socio")
        self.btn_agregar.clicked.disconnect()
        self.btn_agregar.clicked.connect(self.agregar_socio)
        
        # Limpiar campos
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_telefono.clear()
        
        QMessageBox.information(self, "Éxito", "Socio actualizado correctamente.")

    def eliminar_socio(self):
        """Elimina el socio seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un socio para eliminar.")
            return

        socio_id = int(self.tabla.item(fila, 0).text())
        nombre = self.tabla.item(fila, 1).text()
        apellido = self.tabla.item(fila, 2).text()
        
        reply = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Estás seguro de eliminar a {nombre} {apellido}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.controller.eliminar(socio_id)
            self.cargar_socios()
            QMessageBox.information(self, "Éxito", "Socio eliminado correctamente.")