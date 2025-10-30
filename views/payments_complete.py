'''"""
views/payments_complete.py
Vista completa y mejorada para la gestión de pagos de socios.
Incluye: registro, edición, eliminación, búsqueda avanzada, estadísticas y exportación.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QGroupBox, QFormLayout, QTextEdit, QDialog, QDialogButtonBox,
    QDateEdit, QDoubleSpinBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont
from datetime import datetime, timedelta


class PaymentsCompleteView(QWidget):
    def __init__(self, controller, email_service=None):
        super().__init__()
        self.controller = controller
        self.email_service = email_service
        self.pago_seleccionado = None
        self.init_ui()
        
        # Auto-actualizar cada 60 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(60000)

    def init_ui(self):
        # Crear scroll area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)

        # === TÍTULO ===
        title = QLabel("💰 Gestión de Pagos de Socios")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0078d7;
            padding: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # === ESTADÍSTICAS RÁPIDAS ===
        stats_group = QGroupBox("📊 Resumen del Mes Actual")
        stats_layout = QHBoxLayout()
        
        mes_actual_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        mes_actual_fin = datetime.now().strftime('%Y-%m-%d')
        stats = self.controller.obtener_estadisticas(mes_actual_inicio, mes_actual_fin)
        
        self.card_total_mes = self._crear_card("Total del Mes", f"${stats['total_ingresos']:,.0f}", "#4CAF50")
        self.card_pagos_mes = self._crear_card("Pagos Registrados", str(stats['total_pagos']), "#2196F3")
        self.card_socios_mes = self._crear_card("Socios que Pagaron", str(stats['socios_pagaron']), "#FF9800")
        self.card_promedio = self._crear_card("Promedio", f"${stats['promedio_pago']:,.0f}", "#9C27B0")
        
        stats_layout.addWidget(self.card_total_mes)
        stats_layout.addWidget(self.card_pagos_mes)
        stats_layout.addWidget(self.card_socios_mes)
        stats_layout.addWidget(self.card_promedio)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # === FORMULARIO DE REGISTRO RÁPIDO ===
        form_group = QGroupBox("➕ Registrar Nuevo Pago")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 3px solid #28a745;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #28a745;
                padding: 5px;
            }
        """)
        form_layout = QHBoxLayout()

        # Socio
        self.cmb_socio = QComboBox()
        self.cmb_socio.setMinimumWidth(200)
        self.cargar_socios()

        # Monto
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 1000000)
        self.spin_monto.setPrefix("$ ")
        self.spin_monto.setValue(5000)
        self.spin_monto.setSingleStep(100)

        # Mes correspondiente
        self.cmb_mes = QComboBox()
        self.cargar_meses()

        # Método de pago
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["Efectivo", "Transferencia", "Débito", "Crédito", "MercadoPago", "Otro"])

        # Botón registrar
        btn_registrar = QPushButton("✅ Registrar Pago")
        btn_registrar.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #28a745;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        btn_registrar.clicked.connect(self.registrar_pago_rapido)

        form_layout.addWidget(QLabel("Socio:"))
        form_layout.addWidget(self.cmb_socio)
        form_layout.addWidget(QLabel("Monto:"))
        form_layout.addWidget(self.spin_monto)
        form_layout.addWidget(QLabel("Mes:"))
        form_layout.addWidget(self.cmb_mes)
        form_layout.addWidget(QLabel("Método:"))
        form_layout.addWidget(self.cmb_metodo)
        form_layout.addWidget(btn_registrar)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # === FILTROS DE BÚSQUEDA ===
        filtros_group = QGroupBox("🔍 Filtros de Búsqueda")
        filtros_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #0078d7;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout()

        # Filtro por socio
        self.cmb_filtro_socio = QComboBox()
        self.cmb_filtro_socio.addItem("Todos los socios", None)
        self.cargar_socios_filtro()

        # Filtro por mes
        self.cmb_filtro_mes = QComboBox()
        self.cmb_filtro_mes.addItem("Todos los meses", "")
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        for i, mes in enumerate(meses, 1):
            self.cmb_filtro_mes.addItem(mes, str(i).zfill(2))

        # Filtro por año
        self.cmb_filtro_anio = QComboBox()
        self.cmb_filtro_anio.addItem("Todos los años", "")
        anio_actual = datetime.now().year
        for anio in range(anio_actual - 5, anio_actual + 1):
            self.cmb_filtro_anio.addItem(str(anio), str(anio))
        self.cmb_filtro_anio.setCurrentText(str(anio_actual))

        # Botones de filtro
        btn_aplicar_filtros = QPushButton("🔎 Buscar")
        btn_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        btn_aplicar_filtros.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #2196F3;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)

        btn_limpiar = QPushButton("🔄 Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_filtros)
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

        filtros_layout.addWidget(QLabel("Socio:"))
        filtros_layout.addWidget(self.cmb_filtro_socio)
        filtros_layout.addWidget(QLabel("Mes:"))
        filtros_layout.addWidget(self.cmb_filtro_mes)
        filtros_layout.addWidget(QLabel("Año:"))
        filtros_layout.addWidget(self.cmb_filtro_anio)
        filtros_layout.addWidget(btn_aplicar_filtros)
        filtros_layout.addWidget(btn_limpiar)
        filtros_layout.addStretch()

        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # === TABLA DE PAGOS ===
        tabla_group = QGroupBox("📋 Historial de Pagos")
        tabla_layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Socio", "Monto", "Fecha de Pago", "Mes Correspondiente", 
            "Método", "Observaciones", "Acciones"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setColumnWidth(0, 50)
        self.tabla.setColumnWidth(1, 180)
        self.tabla.setColumnWidth(2, 100)
        self.tabla.setColumnWidth(3, 120)
        self.tabla.setColumnWidth(4, 140)
        self.tabla.setColumnWidth(5, 120)
        self.tabla.setMinimumHeight(300)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #0078d7;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: black;
            }
        """)

        tabla_layout.addWidget(self.tabla)
        tabla_group.setLayout(tabla_layout)
        layout.addWidget(tabla_group)

        # === BOTONES DE ACCIÓN ===
        btn_layout = QHBoxLayout()

        self.btn_editar = QPushButton("✏️ Editar Pago")
        self.btn_editar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #ffc107;
                color: #333;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        self.btn_editar.clicked.connect(self.editar_pago)

        self.btn_eliminar = QPushButton("🗑️ Eliminar Pago")
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #dc3545;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_pago)

        self.btn_ver_historial = QPushButton("📜 Ver Historial Completo")
        self.btn_ver_historial.clicked.connect(self.ver_historial_socio)
        self.btn_ver_historial.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #9C27B0;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
        """)

        self.btn_exportar = QPushButton("📊 Exportar a CSV")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #388E3C;
            }
        """)

        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_ver_historial)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_exportar)

        layout.addLayout(btn_layout)

        scroll.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Cargar datos iniciales
        self.cargar_pagos()

    def _crear_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-top: 5px solid {color};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 13px; color: #666; font-weight: 500;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        frame.lbl_valor = lbl_valor
        return frame

    def cargar_socios(self):
        """Carga los socios en el combo de registro."""
        self.cmb_socio.clear()
        socios = self.controller.obtener_socios()
        for socio in socios:
            self.cmb_socio.addItem(f"{socio[1]} {socio[2]}", socio[0])

    def cargar_socios_filtro(self):
        """Carga los socios en el combo de filtro."""
        socios = self.controller.obtener_socios()
        for socio in socios:
            self.cmb_filtro_socio.addItem(f"{socio[1]} {socio[2]}", socio[0])

    def cargar_meses(self):
        """Carga los meses en el combo."""
        self.cmb_mes.clear()
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        anio_actual = datetime.now().year
        mes_actual = datetime.now().month
        
        for i, mes in enumerate(meses, 1):
            mes_valor = f"{anio_actual}-{str(i).zfill(2)}"
            self.cmb_mes.addItem(f"{mes} {anio_actual}", mes_valor)
        
        # Seleccionar mes actual
        self.cmb_mes.setCurrentIndex(mes_actual - 1)

    def cargar_pagos(self):
        """Carga todos los pagos en la tabla."""
        pagos = self.controller.obtener_todos_los_pagos()
        self._mostrar_pagos(pagos)

    def _mostrar_pagos(self, pagos):
        """Muestra los pagos en la tabla."""
        self.tabla.setRowCount(len(pagos))

        for row, pago in enumerate(pagos):
            # ID
            self.tabla.setItem(row, 0, QTableWidgetItem(str(pago[0])))
            
            # Socio
            self.tabla.setItem(row, 1, QTableWidgetItem(pago[1]))
            
            # Monto
            item_monto = QTableWidgetItem(f"${pago[2]:,.2f}")
            item_monto.setForeground(QColor(76, 175, 80))
            self.tabla.setItem(row, 2, item_monto)
            
            # Fecha de pago
            self.tabla.setItem(row, 3, QTableWidgetItem(pago[3]))
            
            # Mes correspondiente
            self.tabla.setItem(row, 4, QTableWidgetItem(pago[4]))
            
            # Método
            self.tabla.setItem(row, 5, QTableWidgetItem(pago[5] if pago[5] else "Efectivo"))
            
            # Observaciones
            self.tabla.setItem(row, 6, QTableWidgetItem(pago[6] if pago[6] else "-"))

    def registrar_pago_rapido(self):
        """Registra un pago rápido desde el formulario."""
        socio_id = self.cmb_socio.currentData()
        monto = self.spin_monto.value()
        mes = self.cmb_mes.currentData()
        metodo = self.cmb_metodo.currentText().lower()

        if not socio_id:
            QMessageBox.warning(self, "Error", "Seleccioná un socio")
            return

        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
            return

        # Verificar duplicado
        if self.controller.verificar_duplicado(socio_id, mes):
            reply = QMessageBox.question(
                self, "Pago Duplicado",
                f"Ya existe un pago registrado para este mes.\n¿Deseas registrarlo de todas formas?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        try:
            self.controller.registrar_pago(socio_id, monto, mes, metodo, "")
            QMessageBox.information(self, "✅ Éxito", "Pago registrado correctamente")
            
            # Recargar datos
            self.cargar_pagos()
            self.actualizar_estadisticas()
            
            # Limpiar formulario
            self.spin_monto.setValue(5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar pago:\n{str(e)}")

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        socio_id = self.cmb_filtro_socio.currentData()
        mes = self.cmb_filtro_mes.currentData()
        anio = self.cmb_filtro_anio.currentData()

        pagos = self.controller.buscar_pagos(socio_id=socio_id, mes=mes, anio=anio)
        self._mostrar_pagos(pagos)

    def limpiar_filtros(self):
        """Limpia los filtros."""
        self.cmb_filtro_socio.setCurrentIndex(0)
        self.cmb_filtro_mes.setCurrentIndex(0)
        self.cmb_filtro_anio.setCurrentIndex(0)
        self.cargar_pagos()

    def editar_pago(self):
        """Edita el pago seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un pago para editar")
            return

        pago_id = int(self.tabla.item(fila, 0).text())
        pago = self.controller.obtener_pago(pago_id)

        if not pago:
            QMessageBox.warning(self, "Error", "Pago no encontrado")
            return

        # Abrir diálogo de edición
        dialogo = EditarPagoDialog(pago, self)
        if dialogo.exec() == QDialog.Accepted:
            try:
                monto, mes, metodo, obs = dialogo.obtener_datos()
                self.controller.actualizar_pago(pago_id, monto, mes, metodo, obs)
                QMessageBox.information(self, "✅ Éxito", "Pago actualizado correctamente")
                self.cargar_pagos()
                self.actualizar_estadisticas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar:\n{str(e)}")

    def eliminar_pago(self):
        """Elimina el pago seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un pago para eliminar")
            return

        pago_id = int(self.tabla.item(fila, 0).text())
        socio = self.tabla.item(fila, 1).text()
        monto = self.tabla.item(fila, 2).text()

        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar el pago de {socio} por {monto}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.controller.eliminar_pago(pago_id)
                QMessageBox.information(self, "✅ Éxito", "Pago eliminado correctamente")
                self.cargar_pagos()
                self.actualizar_estadisticas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar:\n{str(e)}")

    def ver_historial_socio(self):
        """Muestra el historial completo del socio seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un pago de la tabla")
            return

        # Obtener socio_id del pago seleccionado
        pagos = self.controller.obtener_todos_los_pagos()
        if fila < len(pagos):
            socio_id = pagos[fila][7]  # socio_id está en índice 7
            socio_nombre = pagos[fila][1]
            
            dialogo = HistorialSocioDialog(self.controller, socio_id, socio_nombre, self)
            dialogo.exec()

    def exportar_csv(self):
        """Exporta los pagos a CSV."""
        try:
            import csv
            filename = f"pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Encabezados
                headers = []
                for col in range(self.tabla.columnCount() - 1):  # Excluir columna Acciones
                    headers.append(self.tabla.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Datos
                for row in range(self.tabla.rowCount()):
                    row_data = []
                    for col in range(self.tabla.columnCount() - 1):
                        item = self.tabla.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "✅ Éxito", f"Datos exportados a:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las tarjetas de estadísticas."""
        mes_actual_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        mes_actual_fin = datetime.now().strftime('%Y-%m-%d')
        stats = self.controller.obtener_estadisticas(mes_actual_inicio, mes_actual_fin)
        
        self.card_total_mes.lbl_valor.setText(f"${stats['total_ingresos']:,.0f}")
        self.card_pagos_mes.lbl_valor.setText(str(stats['total_pagos']))
        self.card_socios_mes.lbl_valor.setText(str(stats['socios_pagaron']))
        self.card_promedio.lbl_valor.setText(f"${stats['promedio_pago']:,.0f}")

    def actualizar_datos(self):
        """Actualiza todos los datos."""
        self.cargar_pagos()
        self.actualizar_estadisticas()

    def closeEvent(self, event):
        """Detiene el timer al cerrar."""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()


class EditarPagoDialog(QDialog):
    """Diálogo para editar un pago existente."""
    
    def __init__(self, pago, parent=None):
        super().__init__(parent)
        self.pago = pago
        self.setWindowTitle("Editar Pago")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Monto
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 1000000)
        self.spin_monto.setPrefix("$ ")
        self.spin_monto.setValue(float(self.pago[3]))

        # Mes correspondiente
        self.txt_mes = QLineEdit(self.pago[5])

        # Método de pago
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["efectivo", "transferencia", "débito", "crédito", "mercadopago", "otro"])
        metodo_actual = self.pago[6].lower() if self.pago[6] else "efectivo"
        idx = self.cmb_metodo.findText(metodo_actual, Qt.MatchFixedString)
        if idx >= 0:
            self.cmb_metodo.setCurrentIndex(idx)

        # Observaciones
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlainText(self.pago[7] if self.pago[7] else "")
        self.txt_obs.setMaximumHeight(100)

        layout.addRow("Monto:", self.spin_monto)
        layout.addRow("Mes:", self.txt_mes)
        layout.addRow("Método:", self.cmb_metodo)
        layout.addRow("Observaciones:", self.txt_obs)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def obtener_datos(self):
        """Retorna los datos editados."""
        return (
            self.spin_monto.value(),
            self.txt_mes.text(),
            self.cmb_metodo.currentText(),
            self.txt_obs.toPlainText()
        )


class HistorialSocioDialog(QDialog):
    """Diálogo para ver el historial completo de pagos de un socio."""
    
    def __init__(self, controller, socio_id, socio_nombre, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.socio_id = socio_id
        self.socio_nombre = socio_nombre
        self.setWindowTitle(f"Historial de Pagos - {socio_nombre}")
        self.setMinimumSize(900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título con mejor diseño
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
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        nombre_label = QLabel(self.socio_nombre)
        nombre_label.setStyleSheet("""
            font-size: 16px;
            color: white;
            margin-top: 5px;
        """)
        nombre_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title)
        title_layout.addWidget(nombre_label)
        layout.addWidget(title_frame)

        # Tabla con altura fija
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha de Pago", "Monto", "Mes Correspondiente", "Método", "Observaciones"
        ])
        
        # IMPORTANTE: Establecer altura mínima
        self.tabla.setMinimumHeight(300)
        
        # Configuración de columnas
        self.tabla.setColumnWidth(0, 130)
        self.tabla.setColumnWidth(1, 120)
        self.tabla.setColumnWidth(2, 150)
        self.tabla.setColumnWidth(3, 120)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        
        # Estilos mejorados
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SingleSelection)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 2px solid #2196F3;
                border-radius: 8px;
                background-color: white;
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
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #bbdefb;
                color: black;
            }
            QTableWidget::item:alternate {
                background-color: #f5f5f5;
            }
        """)

        # Cargar datos
        pagos = self.controller.obtener_pagos_socio(self.socio_id)
        self.tabla.setRowCount(len(pagos))

        if len(pagos) == 0:
            # Mostrar mensaje si no hay pagos
            self.tabla.setRowCount(1)
            msg_item = QTableWidgetItem("No hay pagos registrados para este socio")
            msg_item.setForeground(QColor(150, 150, 150))
            msg_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(0, 0, msg_item)
            self.tabla.setSpan(0, 0, 1, 5)

        total_pagado = 0
        for row, pago in enumerate(pagos):
            # Fecha de pago
            fecha_item = QTableWidgetItem(pago[2])
            fecha_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(row, 0, fecha_item)
            
            # Monto
            monto = float(pago[1])
            total_pagado += monto
            item_monto = QTableWidgetItem(f"${monto:,.2f}")
            item_monto.setForeground(QColor(76, 175, 80))
            item_monto.setTextAlignment(Qt.AlignCenter)
            font = QFont("Arial", 10, QFont.Bold)
            item_monto.setFont(font)
            self.tabla.setItem(row, 1, item_monto)
            
            # Mes correspondiente
            mes_item = QTableWidgetItem(pago[3])
            mes_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(row, 2, mes_item)
            
            # Método
            metodo = pago[4] if pago[4] else "Efectivo"
            metodo_item = QTableWidgetItem(metodo.capitalize())
            metodo_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(row, 3, metodo_item)
            
            # Observaciones
            obs = pago[5] if pago[5] else "-"
            obs_item = QTableWidgetItem(obs)
            self.tabla.setItem(row, 4, obs_item)

        # Ajustar altura de filas
        self.tabla.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.tabla)

        # Estadísticas del socio con diseño mejorado
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: white;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(30)

        # Tarjeta Total Pagado
        card_total = self._crear_stat_card(
            "💰 Total Pagado", 
            f"${total_pagado:,.2f}",
            "#4CAF50"
        )
        
        # Tarjeta Cantidad de Pagos
        card_cantidad = self._crear_stat_card(
            "📊 Cantidad de Pagos",
            str(len(pagos)),
            "#2196F3"
        )

        # Tarjeta Promedio
        promedio = total_pagado / len(pagos) if len(pagos) > 0 else 0
        card_promedio = self._crear_stat_card(
            "📈 Promedio por Pago",
            f"${promedio:,.2f}",
            "#FF9800"
        )

        stats_layout.addWidget(card_total)
        stats_layout.addWidget(card_cantidad)
        stats_layout.addWidget(card_promedio)

        layout.addWidget(stats_frame)

        # Botón cerrar con mejor diseño
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
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
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #0D47A1;
            }
        """)
        
        btn_layout.addWidget(btn_cerrar)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _crear_stat_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 5px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(5)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("""
            font-size: 12px;
            color: #666;
            font-weight: 500;
        """)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {color};
        """)
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        return frame'''
"""
views/payments_complete.py
Vista completa y mejorada para la gestión de pagos de socios.
Incluye: registro, edición, eliminación, búsqueda avanzada, estadísticas y exportación.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QHBoxLayout, QPushButton, QComboBox, QLineEdit, QMessageBox,
    QGroupBox, QFormLayout, QTextEdit, QDialog, QDialogButtonBox,
    QDateEdit, QDoubleSpinBox, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QColor, QFont
from datetime import datetime, timedelta


class PaymentsCompleteView(QWidget):
    def __init__(self, controller, email_service=None):
        super().__init__()
        self.controller = controller
        self.email_service = email_service
        self.pago_seleccionado = None
        self.init_ui()
        
        # Auto-actualizar cada 60 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_datos)
        self.timer.start(60000)

    def init_ui(self):
        # Crear scroll area principal
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)

        # === TÍTULO ===
        title = QLabel("💰 Gestión de Pagos de Socios")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #0078d7;
            padding: 15px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # === ESTADÍSTICAS RÁPIDAS ===
        stats_group = QGroupBox("📊 Resumen del Mes Actual")
        stats_layout = QHBoxLayout()
        
        mes_actual_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        mes_actual_fin = datetime.now().strftime('%Y-%m-%d')
        stats = self.controller.obtener_estadisticas(mes_actual_inicio, mes_actual_fin)
        
        self.card_total_mes = self._crear_card("Total del Mes", f"${stats['total_ingresos']:,.0f}", "#4CAF50")
        self.card_pagos_mes = self._crear_card("Pagos Registrados", str(stats['total_pagos']), "#2196F3")
        self.card_socios_mes = self._crear_card("Socios que Pagaron", str(stats['socios_pagaron']), "#FF9800")
        self.card_promedio = self._crear_card("Promedio", f"${stats['promedio_pago']:,.0f}", "#9C27B0")
        
        stats_layout.addWidget(self.card_total_mes)
        stats_layout.addWidget(self.card_pagos_mes)
        stats_layout.addWidget(self.card_socios_mes)
        stats_layout.addWidget(self.card_promedio)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # === FORMULARIO DE REGISTRO RÁPIDO ===
        form_group = QGroupBox("➕ Registrar Nuevo Pago")
        form_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 3px solid #28a745;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #28a745;
                padding: 5px;
            }
        """)
        form_layout = QHBoxLayout()

        # Socio
        self.cmb_socio = QComboBox()
        self.cmb_socio.setMinimumWidth(200)
        self.cargar_socios()

        # Monto
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 1000000)
        self.spin_monto.setPrefix("$ ")
        self.spin_monto.setValue(5000)
        self.spin_monto.setSingleStep(100)

        # Mes correspondiente
        self.cmb_mes = QComboBox()
        self.cargar_meses()

        # Método de pago
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["Efectivo", "Transferencia", "Débito", "Crédito", "MercadoPago", "Otro"])

        # Botón registrar
        btn_registrar = QPushButton("✅ Registrar Pago")
        btn_registrar.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #28a745;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #218838;
            }
        """)
        btn_registrar.clicked.connect(self.registrar_pago_rapido)

        form_layout.addWidget(QLabel("Socio:"))
        form_layout.addWidget(self.cmb_socio)
        form_layout.addWidget(QLabel("Monto:"))
        form_layout.addWidget(self.spin_monto)
        form_layout.addWidget(QLabel("Mes:"))
        form_layout.addWidget(self.cmb_mes)
        form_layout.addWidget(QLabel("Método:"))
        form_layout.addWidget(self.cmb_metodo)
        form_layout.addWidget(btn_registrar)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # === FILTROS DE BÚSQUEDA ===
        filtros_group = QGroupBox("🔍 Filtros de Búsqueda")
        filtros_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #0078d7;
                border-radius: 8px;
                margin-top: 10px;
                padding: 15px;
            }
            QGroupBox::title {
                color: #0078d7;
                padding: 5px;
            }
        """)
        filtros_layout = QHBoxLayout()

        # Filtro por socio
        self.cmb_filtro_socio = QComboBox()
        self.cmb_filtro_socio.addItem("Todos los socios", None)
        self.cargar_socios_filtro()

        # Filtro por mes
        self.cmb_filtro_mes = QComboBox()
        self.cmb_filtro_mes.addItem("Todos los meses", "")
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        for i, mes in enumerate(meses, 1):
            self.cmb_filtro_mes.addItem(mes, str(i).zfill(2))

        # Filtro por año
        self.cmb_filtro_anio = QComboBox()
        self.cmb_filtro_anio.addItem("Todos los años", "")
        anio_actual = datetime.now().year
        for anio in range(anio_actual - 5, anio_actual + 1):
            self.cmb_filtro_anio.addItem(str(anio), str(anio))
        self.cmb_filtro_anio.setCurrentText(str(anio_actual))

        # Botones de filtro
        btn_aplicar_filtros = QPushButton("🔎 Buscar")
        btn_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        btn_aplicar_filtros.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #2196F3;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)

        btn_limpiar = QPushButton("🔄 Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_filtros)
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

        filtros_layout.addWidget(QLabel("Socio:"))
        filtros_layout.addWidget(self.cmb_filtro_socio)
        filtros_layout.addWidget(QLabel("Mes:"))
        filtros_layout.addWidget(self.cmb_filtro_mes)
        filtros_layout.addWidget(QLabel("Año:"))
        filtros_layout.addWidget(self.cmb_filtro_anio)
        filtros_layout.addWidget(btn_aplicar_filtros)
        filtros_layout.addWidget(btn_limpiar)
        filtros_layout.addStretch()

        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # === TABLA DE PAGOS ===
        tabla_group = QGroupBox("📋 Historial de Pagos")
        tabla_layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(8)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Socio", "Monto", "Fecha de Pago", "Mes Correspondiente", 
            "Método", "Observaciones", "Acciones"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabla.setColumnWidth(0, 50)
        self.tabla.setColumnWidth(1, 180)
        self.tabla.setColumnWidth(2, 100)
        self.tabla.setColumnWidth(3, 120)
        self.tabla.setColumnWidth(4, 140)
        self.tabla.setColumnWidth(5, 120)
        self.tabla.setMinimumHeight(300)
        self.tabla.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 6px;
                background-color: transparent;
            }
            QHeaderView::section {
                background-color: #0078d7;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #cce5ff;
                color: black;
            }
            QTableWidget::item:alternate {
                background-color: rgba(245, 245, 245, 0.3);
            }
        """)

        tabla_layout.addWidget(self.tabla)
        tabla_group.setLayout(tabla_layout)
        layout.addWidget(tabla_group)

        # === BOTONES DE ACCIÓN ===
        btn_layout = QHBoxLayout()

        self.btn_editar = QPushButton("✏️ Editar Pago")
        self.btn_editar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #ffc107;
                color: #333;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #e0a800;
            }
        """)
        self.btn_editar.clicked.connect(self.editar_pago)

        self.btn_eliminar = QPushButton("🗑️ Eliminar Pago")
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #dc3545;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c82333;
            }
        """)
        self.btn_eliminar.clicked.connect(self.eliminar_pago)

        self.btn_ver_historial = QPushButton("📜 Ver Historial Completo")
        self.btn_ver_historial.clicked.connect(self.ver_historial_socio)
        self.btn_ver_historial.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #9C27B0;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
        """)

        self.btn_exportar = QPushButton("📊 Exportar a CSV")
        self.btn_exportar.clicked.connect(self.exportar_csv)
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #388E3C;
            }
        """)

        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_ver_historial)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_exportar)

        layout.addLayout(btn_layout)

        scroll.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Cargar datos iniciales
        self.cargar_pagos()

    def _crear_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-top: 5px solid {color};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 13px; color: #666; font-weight: 500;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        frame.lbl_valor = lbl_valor
        return frame

    def cargar_socios(self):
        """Carga los socios en el combo de registro."""
        self.cmb_socio.clear()
        socios = self.controller.obtener_socios()
        for socio in socios:
            self.cmb_socio.addItem(f"{socio[1]} {socio[2]}", socio[0])

    def cargar_socios_filtro(self):
        """Carga los socios en el combo de filtro."""
        socios = self.controller.obtener_socios()
        for socio in socios:
            self.cmb_filtro_socio.addItem(f"{socio[1]} {socio[2]}", socio[0])

    def cargar_meses(self):
        """Carga los meses en el combo."""
        self.cmb_mes.clear()
        meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                 "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        anio_actual = datetime.now().year
        mes_actual = datetime.now().month
        
        for i, mes in enumerate(meses, 1):
            mes_valor = f"{anio_actual}-{str(i).zfill(2)}"
            self.cmb_mes.addItem(f"{mes} {anio_actual}", mes_valor)
        
        # Seleccionar mes actual
        self.cmb_mes.setCurrentIndex(mes_actual - 1)

    def cargar_pagos(self):
        """Carga todos los pagos en la tabla."""
        pagos = self.controller.obtener_todos_los_pagos()
        self._mostrar_pagos(pagos)

    def _mostrar_pagos(self, pagos):
        """Muestra los pagos en la tabla."""
        self.tabla.setRowCount(len(pagos))

        for row, pago in enumerate(pagos):
            # ID
            self.tabla.setItem(row, 0, QTableWidgetItem(str(pago[0])))
            
            # Socio
            self.tabla.setItem(row, 1, QTableWidgetItem(pago[1]))
            
            # Monto
            item_monto = QTableWidgetItem(f"${pago[2]:,.2f}")
            item_monto.setForeground(QColor(76, 175, 80))
            self.tabla.setItem(row, 2, item_monto)
            
            # Fecha de pago
            self.tabla.setItem(row, 3, QTableWidgetItem(pago[3]))
            
            # Mes correspondiente
            self.tabla.setItem(row, 4, QTableWidgetItem(pago[4]))
            
            # Método
            self.tabla.setItem(row, 5, QTableWidgetItem(pago[5] if pago[5] else "Efectivo"))
            
            # Observaciones
            self.tabla.setItem(row, 6, QTableWidgetItem(pago[6] if pago[6] else "-"))

    def registrar_pago_rapido(self):
        """Registra un pago rápido desde el formulario."""
        socio_id = self.cmb_socio.currentData()
        monto = self.spin_monto.value()
        mes = self.cmb_mes.currentData()
        metodo = self.cmb_metodo.currentText().lower()

        if not socio_id:
            QMessageBox.warning(self, "Error", "Seleccioná un socio")
            return

        if monto <= 0:
            QMessageBox.warning(self, "Error", "El monto debe ser mayor a 0")
            return

        # Verificar duplicado
        if self.controller.verificar_duplicado(socio_id, mes):
            reply = QMessageBox.question(
                self, "Pago Duplicado",
                f"Ya existe un pago registrado para este mes.\n¿Deseas registrarlo de todas formas?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return

        try:
            self.controller.registrar_pago(socio_id, monto, mes, metodo, "")
            QMessageBox.information(self, "✅ Éxito", "Pago registrado correctamente")
            
            # Recargar datos
            self.cargar_pagos()
            self.actualizar_estadisticas()
            
            # Limpiar formulario
            self.spin_monto.setValue(5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al registrar pago:\n{str(e)}")

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        socio_id = self.cmb_filtro_socio.currentData()
        mes = self.cmb_filtro_mes.currentData()
        anio = self.cmb_filtro_anio.currentData()

        pagos = self.controller.buscar_pagos(socio_id=socio_id, mes=mes, anio=anio)
        self._mostrar_pagos(pagos)

    def limpiar_filtros(self):
        """Limpia los filtros."""
        self.cmb_filtro_socio.setCurrentIndex(0)
        self.cmb_filtro_mes.setCurrentIndex(0)
        self.cmb_filtro_anio.setCurrentIndex(0)
        self.cargar_pagos()

    def editar_pago(self):
        """Edita el pago seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un pago para editar")
            return

        pago_id = int(self.tabla.item(fila, 0).text())
        pago = self.controller.obtener_pago(pago_id)

        if not pago:
            QMessageBox.warning(self, "Error", "Pago no encontrado")
            return

        # Abrir diálogo de edición
        dialogo = EditarPagoDialog(pago, self)
        if dialogo.exec() == QDialog.Accepted:
            try:
                monto, mes, metodo, obs = dialogo.obtener_datos()
                self.controller.actualizar_pago(pago_id, monto, mes, metodo, obs)
                QMessageBox.information(self, "✅ Éxito", "Pago actualizado correctamente")
                self.cargar_pagos()
                self.actualizar_estadisticas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar:\n{str(e)}")

    def eliminar_pago(self):
        """Elimina el pago seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un pago para eliminar")
            return

        pago_id = int(self.tabla.item(fila, 0).text())
        socio = self.tabla.item(fila, 1).text()
        monto = self.tabla.item(fila, 2).text()

        reply = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Eliminar el pago de {socio} por {monto}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.controller.eliminar_pago(pago_id)
                QMessageBox.information(self, "✅ Éxito", "Pago eliminado correctamente")
                self.cargar_pagos()
                self.actualizar_estadisticas()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar:\n{str(e)}")

    def ver_historial_socio(self):
        """Muestra el historial completo del socio seleccionado."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná un pago de la tabla")
            return

        # Obtener socio_id del pago seleccionado
        pagos = self.controller.obtener_todos_los_pagos()
        if fila < len(pagos):
            socio_id = pagos[fila][7]  # socio_id está en índice 7
            socio_nombre = pagos[fila][1]
            
            dialogo = HistorialSocioDialog(self.controller, socio_id, socio_nombre, self)
            dialogo.exec()

    def exportar_csv(self):
        """Exporta los pagos a CSV."""
        try:
            import csv
            filename = f"pagos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Encabezados
                headers = []
                for col in range(self.tabla.columnCount() - 1):  # Excluir columna Acciones
                    headers.append(self.tabla.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Datos
                for row in range(self.tabla.rowCount()):
                    row_data = []
                    for col in range(self.tabla.columnCount() - 1):
                        item = self.tabla.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(self, "✅ Éxito", f"Datos exportados a:\n{filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar:\n{str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las tarjetas de estadísticas."""
        mes_actual_inicio = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        mes_actual_fin = datetime.now().strftime('%Y-%m-%d')
        stats = self.controller.obtener_estadisticas(mes_actual_inicio, mes_actual_fin)
        
        self.card_total_mes.lbl_valor.setText(f"${stats['total_ingresos']:,.0f}")
        self.card_pagos_mes.lbl_valor.setText(str(stats['total_pagos']))
        self.card_socios_mes.lbl_valor.setText(str(stats['socios_pagaron']))
        self.card_promedio.lbl_valor.setText(f"${stats['promedio_pago']:,.0f}")

    def actualizar_datos(self):
        """Actualiza todos los datos."""
        self.cargar_pagos()
        self.actualizar_estadisticas()

    def closeEvent(self, event):
        """Detiene el timer al cerrar."""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()


class EditarPagoDialog(QDialog):
    """Diálogo para editar un pago existente."""
    
    def __init__(self, pago, parent=None):
        super().__init__(parent)
        self.pago = pago
        self.setWindowTitle("Editar Pago")
        self.setMinimumWidth(500)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        # Monto
        self.spin_monto = QDoubleSpinBox()
        self.spin_monto.setRange(0, 1000000)
        self.spin_monto.setPrefix("$ ")
        self.spin_monto.setValue(float(self.pago[3]))

        # Mes correspondiente
        self.txt_mes = QLineEdit(self.pago[5])

        # Método de pago
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["efectivo", "transferencia", "débito", "crédito", "mercadopago", "otro"])
        metodo_actual = self.pago[6].lower() if self.pago[6] else "efectivo"
        idx = self.cmb_metodo.findText(metodo_actual, Qt.MatchFixedString)
        if idx >= 0:
            self.cmb_metodo.setCurrentIndex(idx)

        # Observaciones
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlainText(self.pago[7] if self.pago[7] else "")
        self.txt_obs.setMaximumHeight(100)

        layout.addRow("Monto:", self.spin_monto)
        layout.addRow("Mes:", self.txt_mes)
        layout.addRow("Método:", self.cmb_metodo)
        layout.addRow("Observaciones:", self.txt_obs)

        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def obtener_datos(self):
        """Retorna los datos editados."""
        return (
            self.spin_monto.value(),
            self.txt_mes.text(),
            self.cmb_metodo.currentText(),
            self.txt_obs.toPlainText()
        )


class HistorialSocioDialog(QDialog):
    """Diálogo para ver el historial completo de pagos de un socio."""
    
    def __init__(self, controller, socio_id, socio_nombre, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.socio_id = socio_id
        self.socio_nombre = socio_nombre
        self.setWindowTitle(f"Historial de Pagos - {socio_nombre}")
        self.setMinimumSize(900, 600)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título con mejor diseño
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
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
        """)
        title.setAlignment(Qt.AlignCenter)
        
        nombre_label = QLabel(self.socio_nombre)
        nombre_label.setStyleSheet("""
            font-size: 16px;
            color: white;
            margin-top: 5px;
        """)
        nombre_label.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(title)
        title_layout.addWidget(nombre_label)
        layout.addWidget(title_frame)

        # Tabla con altura fija
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha de Pago", "Monto", "Mes Correspondiente", "Método", "Observaciones"
        ])
        
        # IMPORTANTE: Establecer altura mínima
        self.tabla.setMinimumHeight(300)
        
        # Configuración de columnas
        self.tabla.setColumnWidth(0, 130)
        self.tabla.setColumnWidth(1, 120)
        self.tabla.setColumnWidth(2, 150)
        self.tabla.setColumnWidth(3, 120)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        
        # Estilos mejorados
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
            QTableWidget::item {
                padding: 8px;
                background-color: transparent;
            }
            QTableWidget::item:selected {
                background-color: #bbdefb;
                color: black;
            }
            QTableWidget::item:alternate {
                background-color: rgba(245, 245, 245, 0.3);
            }
        """)

        # Cargar datos
        pagos = self.controller.obtener_pagos_socio(self.socio_id)
        self.tabla.setRowCount(len(pagos))

        if len(pagos) == 0:
            # Mostrar mensaje si no hay pagos
            self.tabla.setRowCount(1)
            msg_item = QTableWidgetItem("No hay pagos registrados para este socio")
            msg_item.setForeground(QColor(150, 150, 150))
            msg_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(0, 0, msg_item)
            self.tabla.setSpan(0, 0, 1, 5)

        total_pagado = 0
        for row, pago in enumerate(pagos):
            # Fecha de pago
            fecha_item = QTableWidgetItem(pago[2])
            fecha_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(row, 0, fecha_item)
            
            # Monto
            monto = float(pago[1])
            total_pagado += monto
            item_monto = QTableWidgetItem(f"${monto:,.2f}")
            item_monto.setForeground(QColor(76, 175, 80))
            item_monto.setTextAlignment(Qt.AlignCenter)
            font = QFont("Arial", 10, QFont.Bold)
            item_monto.setFont(font)
            self.tabla.setItem(row, 1, item_monto)
            
            # Mes correspondiente
            mes_item = QTableWidgetItem(pago[3])
            mes_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(row, 2, mes_item)
            
            # Método
            metodo = pago[4] if pago[4] else "Efectivo"
            metodo_item = QTableWidgetItem(metodo.capitalize())
            metodo_item.setTextAlignment(Qt.AlignCenter)
            self.tabla.setItem(row, 3, metodo_item)
            
            # Observaciones
            obs = pago[5] if pago[5] else "-"
            obs_item = QTableWidgetItem(obs)
            self.tabla.setItem(row, 4, obs_item)

        # Ajustar altura de filas
        self.tabla.verticalHeader().setDefaultSectionSize(40)

        layout.addWidget(self.tabla)

        # Estadísticas del socio con diseño mejorado
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: 2px solid #4CAF50;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(30)

        # Tarjeta Total Pagado
        card_total = self._crear_stat_card(
            "💰 Total Pagado", 
            f"${total_pagado:,.2f}",
            "#4CAF50"
        )
        
        # Tarjeta Cantidad de Pagos
        card_cantidad = self._crear_stat_card(
            "📊 Cantidad de Pagos",
            str(len(pagos)),
            "#2196F3"
        )

        # Tarjeta Promedio
        promedio = total_pagado / len(pagos) if len(pagos) > 0 else 0
        card_promedio = self._crear_stat_card(
            "📈 Promedio por Pago",
            f"${promedio:,.2f}",
            "#FF9800"
        )

        stats_layout.addWidget(card_total)
        stats_layout.addWidget(card_cantidad)
        stats_layout.addWidget(card_promedio)

        layout.addWidget(stats_frame)

        # Botón cerrar con mejor diseño
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
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
                font-size: 14px;
                border: none;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #0D47A1;
            }
        """)
        
        btn_layout.addWidget(btn_cerrar)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _crear_stat_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: transparent;
                border-left: 5px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(5)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("""
            font-size: 12px;
            color: #666;
            font-weight: 500;
        """)
        lbl_titulo.setAlignment(Qt.AlignCenter)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"""
            font-size: 24px;
            font-weight: bold;
            color: {color};
        """)
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        return frame