"""
views/payments.py
Vista para registrar y consultar pagos de los socios con filtros avanzados.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QComboBox, QLineEdit, QFormLayout, 
    QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from datetime import datetime


class PaymentsView(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("Gestión de Pagos")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:22px; font-weight:600; margin:10px;")
        layout.addWidget(title)

        # --- FILTROS ---
        filtros_group = QGroupBox("🔍 Filtros de Búsqueda")
        filtros_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #0078d7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #0078d7;
            }
        """)
        filtros_layout = QHBoxLayout()

        # Filtro por mes
        lbl_mes = QLabel("Mes:")
        self.cmb_mes = QComboBox()
        self.cmb_mes.addItem("Todos los meses", "")
        meses = [
            "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]
        for i, mes in enumerate(meses, 1):
            self.cmb_mes.addItem(mes, str(i).zfill(2))
        self.cmb_mes.currentIndexChanged.connect(self.aplicar_filtros)

        # Filtro por año
        lbl_anio = QLabel("Año:")
        self.cmb_anio = QComboBox()
        anio_actual = datetime.now().year
        self.cmb_anio.addItem("Todos los años", "")
        for anio in range(anio_actual - 5, anio_actual + 1):
            self.cmb_anio.addItem(str(anio), str(anio))
        self.cmb_anio.setCurrentText(str(anio_actual))
        self.cmb_anio.currentIndexChanged.connect(self.aplicar_filtros)

        # Filtro por socio
        lbl_socio = QLabel("Socio:")
        self.cmb_filtro_socio = QComboBox()
        self.cmb_filtro_socio.addItem("Todos los socios", None)
        self.cmb_filtro_socio.currentIndexChanged.connect(self.aplicar_filtros)

        # Botón limpiar filtros
        btn_limpiar_filtros = QPushButton("🔄 Limpiar Filtros")
        btn_limpiar_filtros.clicked.connect(self.limpiar_filtros)
        btn_limpiar_filtros.setStyleSheet("""
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

        filtros_layout.addWidget(lbl_mes)
        filtros_layout.addWidget(self.cmb_mes)
        filtros_layout.addWidget(lbl_anio)
        filtros_layout.addWidget(self.cmb_anio)
        filtros_layout.addWidget(lbl_socio)
        filtros_layout.addWidget(self.cmb_filtro_socio)
        filtros_layout.addWidget(btn_limpiar_filtros)
        filtros_layout.addStretch()

        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # --- TABLA DE PAGOS ---
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "ID", "Socio", "Monto", "Fecha de Pago", "Mes Correspondiente"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #0078d7;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.table)

        # --- FORMULARIO DE REGISTRO DE PAGO ---
        form_group = QGroupBox("💰 Registrar Nuevo Pago")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #28a745;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #28a745;
            }
        """)
        form_layout = QHBoxLayout()

        self.cmb_socios = QComboBox()
        self.txt_monto = QLineEdit()
        self.txt_monto.setPlaceholderText("Monto (ej: 5000)")
        
        self.txt_mes = QComboBox()
        for i, mes in enumerate(meses, 1):
            mes_valor = f"{datetime.now().year}-{str(i).zfill(2)}"
            self.txt_mes.addItem(f"{mes} {datetime.now().year}", mes_valor)
        # Seleccionar mes actual
        self.txt_mes.setCurrentIndex(datetime.now().month - 1)

        btn_registrar = QPushButton("✅ Registrar Pago")
        btn_registrar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                background: #28a745;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        btn_registrar.clicked.connect(self.registrar_pago)

        form_layout.addWidget(QLabel("Socio:"))
        form_layout.addWidget(self.cmb_socios)
        form_layout.addWidget(QLabel("Monto:"))
        form_layout.addWidget(self.txt_monto)
        form_layout.addWidget(QLabel("Mes:"))
        form_layout.addWidget(self.txt_mes)
        form_layout.addWidget(btn_registrar)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        layout.addStretch()
        self.setLayout(layout)

        # Cargar datos iniciales
        self.cargar_socios()
        self.cargar_socios_filtro()
        self.cargar_pagos()

    def cargar_socios(self):
        """Carga socios en el combo de registro de pago."""
        self.cmb_socios.clear()
        socios = self.controller.obtener_socios()
        for socio in socios:
            self.cmb_socios.addItem(f"{socio[1]} {socio[2]}", socio[0])

    def cargar_socios_filtro(self):
        """Carga socios en el combo de filtro."""
        socio_seleccionado = self.cmb_filtro_socio.currentData()
        self.cmb_filtro_socio.clear()
        self.cmb_filtro_socio.addItem("Todos los socios", None)
        
        socios = self.controller.obtener_socios()
        for socio in socios:
            self.cmb_filtro_socio.addItem(f"{socio[1]} {socio[2]}", socio[0])
        
        # Restaurar selección si existía
        if socio_seleccionado:
            idx = self.cmb_filtro_socio.findData(socio_seleccionado)
            if idx >= 0:
                self.cmb_filtro_socio.setCurrentIndex(idx)

    def cargar_pagos(self):
        """Carga todos los pagos sin filtro."""
        pagos = self.controller.pagos.obtener_pagos()
        self._mostrar_pagos(pagos)

    def _mostrar_pagos(self, pagos):
        """Muestra los pagos en la tabla."""
        self.table.setRowCount(len(pagos))

        for row, pago in enumerate(pagos):
            self.table.setItem(row, 0, QTableWidgetItem(str(pago[0])))
            self.table.setItem(row, 1, QTableWidgetItem(pago[1]))
            self.table.setItem(row, 2, QTableWidgetItem(f"${pago[2]:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(pago[3]))
            self.table.setItem(row, 4, QTableWidgetItem(pago[4]))

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        mes = self.cmb_mes.currentData()
        anio = self.cmb_anio.currentData()
        socio_id = self.cmb_filtro_socio.currentData()

        pagos = self.controller.pagos.obtener_pagos()
        
        # Filtrar por mes
        if mes:
            pagos = [p for p in pagos if mes in p[4]]  # mes_correspondiente
        
        # Filtrar por año
        if anio:
            pagos = [p for p in pagos if anio in p[4]]  # mes_correspondiente
        
        # Filtrar por socio
        if socio_id:
            pagos = [p for p in pagos if p[1] in 
                    [f"{s[1]} {s[2]}" for s in self.controller.obtener_socios() 
                     if s[0] == socio_id]]

        self._mostrar_pagos(pagos)

    def limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.cmb_mes.setCurrentIndex(0)
        self.cmb_anio.setCurrentIndex(0)
        self.cmb_filtro_socio.setCurrentIndex(0)
        self.cargar_pagos()

    def registrar_pago(self):
        """Registra un nuevo pago."""
        socio_id = self.cmb_socios.currentData()
        monto_texto = self.txt_monto.text().strip()
        mes = self.txt_mes.currentData()

        if not monto_texto:
            QMessageBox.warning(self, "Error", "Debés completar el monto.")
            return

        try:
            monto = float(monto_texto)
        except ValueError:
            QMessageBox.warning(self, "Error", "Monto inválido.")
            return

        self.controller.registrar_pago(socio_id, monto, mes)
        QMessageBox.information(self, "Éxito", "Pago registrado correctamente.")
        
        self.cargar_pagos()
        self.txt_monto.clear()