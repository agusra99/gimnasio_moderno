"""
views/reports.py
Vista para generar reportes y estadísticas del gimnasio.
Incluye gráficos, exportación a PDF y Excel.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton,
    QComboBox, QGroupBox, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict


class ReportsView(QWidget):
    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("📊 Reportes y Estadísticas")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Panel de filtros
        filtros_group = QGroupBox("🔍 Seleccionar Período")
        filtros_layout = QHBoxLayout()

        self.combo_periodo = QComboBox()
        self.combo_periodo.addItems([
            "Mes Actual",
            "Mes Anterior",
            "Últimos 3 Meses",
            "Últimos 6 Meses",
            "Año Actual",
            "Año Anterior",
            "Últimos 12 Meses",
            "Todo el Tiempo"
        ])
        self.combo_periodo.currentIndexChanged.connect(self.generar_reporte)

        btn_generar = QPushButton("📈 Generar Reporte")
        btn_generar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #2196F3;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        btn_generar.clicked.connect(self.generar_reporte)

        filtros_layout.addWidget(QLabel("Período:"))
        filtros_layout.addWidget(self.combo_periodo)
        filtros_layout.addWidget(btn_generar)
        filtros_layout.addStretch()
        filtros_group.setLayout(filtros_layout)
        layout.addWidget(filtros_group)

        # Panel de resumen financiero
        resumen_group = QGroupBox("💰 Resumen Financiero")
        resumen_layout = QHBoxLayout()

        self.card_ingresos = self._crear_card("Total Ingresos", "$0", "#4CAF50")
        self.card_socios_pagaron = self._crear_card("Socios que Pagaron", "0", "#2196F3")
        self.card_promedio = self._crear_card("Promedio por Pago", "$0", "#FF9800")

        resumen_layout.addWidget(self.card_ingresos)
        resumen_layout.addWidget(self.card_socios_pagaron)
        resumen_layout.addWidget(self.card_promedio)
        resumen_group.setLayout(resumen_layout)
        layout.addWidget(resumen_group)

        # Panel de estadísticas de socios
        socios_group = QGroupBox("👥 Estadísticas de Socios")
        socios_layout = QHBoxLayout()

        self.card_total_socios = self._crear_card("Total Socios", "0", "#9C27B0")
        self.card_nuevos = self._crear_card("Nuevos en Período", "0", "#00BCD4")
        self.card_activos = self._crear_card("Activos", "0", "#4CAF50")

        socios_layout.addWidget(self.card_total_socios)
        socios_layout.addWidget(self.card_nuevos)
        socios_layout.addWidget(self.card_activos)
        socios_group.setLayout(socios_layout)
        layout.addWidget(socios_group)

        # Tabla de detalles
        detalles_group = QGroupBox("📋 Detalle de Pagos del Período")
        detalles_layout = QVBoxLayout()

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Fecha", "Socio", "Monto", "Mes Correspondiente", "Plan"
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
            }
        """)

        detalles_layout.addWidget(self.tabla)
        detalles_group.setLayout(detalles_layout)
        layout.addWidget(detalles_group)

        # Botones de exportación
        export_layout = QHBoxLayout()

        self.btn_export_excel = QPushButton("📊 Exportar a Excel")
        self.btn_export_excel.setStyleSheet("""
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
        self.btn_export_excel.clicked.connect(self.exportar_excel)

        self.btn_export_pdf = QPushButton("📄 Exportar a PDF")
        self.btn_export_pdf.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #F44336;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #D32F2F;
            }
        """)
        self.btn_export_pdf.clicked.connect(self.exportar_pdf)

        export_layout.addStretch()
        export_layout.addWidget(self.btn_export_excel)
        export_layout.addWidget(self.btn_export_pdf)
        layout.addLayout(export_layout)

        self.setLayout(layout)
        
        # Generar reporte inicial
        self.generar_reporte()

    def _crear_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        from PySide6.QtWidgets import QFrame
        
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 5px solid {color};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"font-size: 14px; color: #666; font-weight: 500;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        frame.lbl_valor = lbl_valor
        return frame

    def _obtener_rango_fechas(self):
        """Obtiene el rango de fechas según el período seleccionado."""
        hoy = datetime.now()
        periodo = self.combo_periodo.currentText()

        if periodo == "Mes Actual":
            inicio = hoy.replace(day=1).strftime('%Y-%m-%d')
            fin = hoy.strftime('%Y-%m-%d')
        elif periodo == "Mes Anterior":
            primer_dia_mes = hoy.replace(day=1)
            ultimo_mes = primer_dia_mes - timedelta(days=1)
            inicio = ultimo_mes.replace(day=1).strftime('%Y-%m-%d')
            fin = ultimo_mes.strftime('%Y-%m-%d')
        elif periodo == "Últimos 3 Meses":
            inicio = (hoy - timedelta(days=90)).strftime('%Y-%m-%d')
            fin = hoy.strftime('%Y-%m-%d')
        elif periodo == "Últimos 6 Meses":
            inicio = (hoy - timedelta(days=180)).strftime('%Y-%m-%d')
            fin = hoy.strftime('%Y-%m-%d')
        elif periodo == "Año Actual":
            inicio = hoy.replace(month=1, day=1).strftime('%Y-%m-%d')
            fin = hoy.strftime('%Y-%m-%d')
        elif periodo == "Año Anterior":
            inicio = hoy.replace(year=hoy.year-1, month=1, day=1).strftime('%Y-%m-%d')
            fin = hoy.replace(year=hoy.year-1, month=12, day=31).strftime('%Y-%m-%d')
        elif periodo == "Últimos 12 Meses":
            inicio = (hoy - timedelta(days=365)).strftime('%Y-%m-%d')
            fin = hoy.strftime('%Y-%m-%d')
        else:  # Todo el Tiempo
            inicio = "2000-01-01"
            fin = hoy.strftime('%Y-%m-%d')

        return inicio, fin

    def generar_reporte(self):
        """Genera el reporte con los datos del período seleccionado."""
        try:
            inicio, fin = self._obtener_rango_fechas()
            
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Ingresos totales del período
            c.execute("""
                SELECT SUM(monto), COUNT(*), COUNT(DISTINCT socio_id)
                FROM pagos
                WHERE fecha_pago BETWEEN ? AND ?
            """, (inicio, fin))
            
            resultado = c.fetchone()
            total_ingresos = resultado[0] if resultado[0] else 0
            cantidad_pagos = resultado[1]
            socios_pagaron = resultado[2]

            # Promedio por pago
            promedio = total_ingresos / cantidad_pagos if cantidad_pagos > 0 else 0

            # Actualizar cards financieros
            self.card_ingresos.lbl_valor.setText(f"${total_ingresos:,.2f}")
            self.card_socios_pagaron.lbl_valor.setText(str(socios_pagaron))
            self.card_promedio.lbl_valor.setText(f"${promedio:,.2f}")

            # Estadísticas de socios
            c.execute("SELECT COUNT(*) FROM socios")
            total_socios = c.fetchone()[0]

            c.execute("""
                SELECT COUNT(*) FROM socios
                WHERE fecha_alta BETWEEN ? AND ?
            """, (inicio, fin))
            nuevos_socios = c.fetchone()[0]

            # Socios activos (con al menos un pago en el período)
            c.execute("""
                SELECT COUNT(DISTINCT socio_id) FROM pagos
                WHERE fecha_pago BETWEEN ? AND ?
            """, (inicio, fin))
            socios_activos = c.fetchone()[0]

            # Actualizar cards de socios
            self.card_total_socios.lbl_valor.setText(str(total_socios))
            self.card_nuevos.lbl_valor.setText(str(nuevos_socios))
            self.card_activos.lbl_valor.setText(str(socios_activos))

            # Cargar detalle de pagos
            c.execute("""
                SELECT p.fecha_pago, s.nombre || ' ' || s.apellido,
                       p.monto, p.mes_correspondiente, pl.nombre
                FROM pagos p
                JOIN socios s ON p.socio_id = s.id
                LEFT JOIN planes pl ON s.plan_id = pl.id
                WHERE p.fecha_pago BETWEEN ? AND ?
                ORDER BY p.fecha_pago DESC
            """, (inicio, fin))

            pagos = c.fetchall()
            self.tabla.setRowCount(len(pagos))

            for row, pago in enumerate(pagos):
                self.tabla.setItem(row, 0, QTableWidgetItem(pago[0]))
                self.tabla.setItem(row, 1, QTableWidgetItem(pago[1]))
                self.tabla.setItem(row, 2, QTableWidgetItem(f"${pago[2]:,.2f}"))
                self.tabla.setItem(row, 3, QTableWidgetItem(pago[3]))
                self.tabla.setItem(row, 4, QTableWidgetItem(pago[4] if pago[4] else "Sin plan"))

            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {str(e)}")

    def exportar_excel(self):
        """Exporta el reporte a Excel."""
        try:
            import csv
            from datetime import datetime
            
            filename = f"reporte_gimnasio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Escribir encabezados
                headers = []
                for col in range(self.tabla.columnCount()):
                    headers.append(self.tabla.horizontalHeaderItem(col).text())
                writer.writerow(headers)
                
                # Escribir datos
                for row in range(self.tabla.rowCount()):
                    row_data = []
                    for col in range(self.tabla.columnCount()):
                        item = self.tabla.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)
            
            QMessageBox.information(
                self,
                "Exportación Exitosa",
                f"Reporte exportado a:\n{filename}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")

    def exportar_pdf(self):
        """Exporta el reporte a PDF."""
        QMessageBox.information(
            self,
            "Próximamente",
            "La exportación a PDF estará disponible próximamente.\n"
            "Por ahora, podés usar la exportación a Excel."
        )