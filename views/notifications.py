"""
views/notifications.py
Vista para gestionar notificaciones y alertas del sistema.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QMessageBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor


class NotificationsView(QWidget):
    def __init__(self, notifications_model):
        super().__init__()
        self.model = notifications_model
        self.init_ui()
        self.cargar_notificaciones()
        
        # Auto-actualizar cada 60 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.cargar_notificaciones)
        self.timer.start(60000)  # 60 segundos

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("🔔 Centro de Notificaciones")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Panel de estadísticas
        stats_group = QGroupBox("📊 Resumen")
        stats_layout = QHBoxLayout()
        
        self.lbl_total = self._crear_stat_card("Total", "0", "#2196F3")
        self.lbl_pendientes = self._crear_stat_card("Pendientes", "0", "#FF9800")
        self.lbl_urgentes = self._crear_stat_card("Urgentes", "0", "#F44336")
        
        stats_layout.addWidget(self.lbl_total)
        stats_layout.addWidget(self.lbl_pendientes)
        stats_layout.addWidget(self.lbl_urgentes)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.btn_verificar = QPushButton("🔄 Verificar Pagos Vencidos")
        self.btn_verificar.setStyleSheet("""
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
        self.btn_verificar.clicked.connect(self.verificar_pagos)
        
        self.btn_limpiar = QPushButton("🧹 Limpiar Antiguas")
        self.btn_limpiar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #9E9E9E;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #757575;
            }
        """)
        self.btn_limpiar.clicked.connect(self.limpiar_antiguas)
        
        self.btn_actualizar = QPushButton("↻ Actualizar")
        self.btn_actualizar.setStyleSheet("""
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
        self.btn_actualizar.clicked.connect(self.cargar_notificaciones)
        
        btn_layout.addWidget(self.btn_verificar)
        btn_layout.addWidget(self.btn_limpiar)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_actualizar)
        layout.addLayout(btn_layout)

        # Tabla de notificaciones
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels([
            "ID", "Socio", "Tipo", "Mensaje", "Fecha", "Prioridad"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(True)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectRows)
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
        layout.addWidget(self.tabla)

        # Botones de gestión
        action_layout = QHBoxLayout()
        
        self.btn_marcar_leida = QPushButton("✓ Marcar como Leída")
        self.btn_marcar_leida.setStyleSheet("""
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
        self.btn_marcar_leida.clicked.connect(self.marcar_leida)
        
        self.btn_marcar_todas = QPushButton("✓✓ Marcar Todas")
        self.btn_marcar_todas.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #FF9800;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        self.btn_marcar_todas.clicked.connect(self.marcar_todas_leidas)
        
        action_layout.addStretch()
        action_layout.addWidget(self.btn_marcar_leida)
        action_layout.addWidget(self.btn_marcar_todas)
        layout.addLayout(action_layout)

        self.setLayout(layout)

    def _crear_stat_card(self, titulo, valor, color):
        """Crea una tarjeta de estadística."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 15px;
            }}
        """)
        
        frame_layout = QVBoxLayout(frame)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet(f"font-size: 14px; color: {color}; font-weight: bold;")
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet("font-size: 28px; font-weight: bold; color: #333;")
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        frame.lbl_valor = lbl_valor
        return frame

    def cargar_notificaciones(self):
        """Carga las notificaciones en la tabla."""
        notificaciones = self.model.obtener_notificaciones_pendientes()
        self.tabla.setRowCount(len(notificaciones))

        for row, notif in enumerate(notificaciones):
            # ID
            self.tabla.setItem(row, 0, QTableWidgetItem(str(notif[0])))
            
            # Socio
            self.tabla.setItem(row, 1, QTableWidgetItem(notif[2]))
            
            # Tipo
            tipo_item = QTableWidgetItem(self._formatear_tipo(notif[3]))
            self.tabla.setItem(row, 2, tipo_item)
            
            # Mensaje
            self.tabla.setItem(row, 3, QTableWidgetItem(notif[4]))
            
            # Fecha
            fecha = notif[5].split()[0] if notif[5] else ""
            self.tabla.setItem(row, 4, QTableWidgetItem(fecha))
            
            # Prioridad
            prioridad_item = QTableWidgetItem(notif[6].upper())
            
            # Colorear según prioridad
            if notif[6] == 'alta':
                color = QColor(244, 67, 54, 50)  # Rojo claro
            elif notif[6] == 'media':
                color = QColor(255, 152, 0, 50)  # Naranja claro
            else:
                color = QColor(33, 150, 243, 50)  # Azul claro
            
            for col in range(6):
                item = self.tabla.item(row, col)
                if item:
                    item.setBackground(color)
            
            self.tabla.setItem(row, 5, prioridad_item)

        # Actualizar estadísticas
        self.actualizar_estadisticas()

    def _formatear_tipo(self, tipo):
        """Formatea el tipo de notificación para mostrar."""
        tipos = {
            'pago_vencido': '⚠️ Pago Vencido',
            'proximo_vencimiento': '⏰ Próximo a Vencer',
            'sin_pagos': '❌ Sin Pagos',
            'renovacion': '🔄 Renovación',
            'otro': 'ℹ️ Información'
        }
        return tipos.get(tipo, tipo)

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas."""
        stats = self.model.obtener_estadisticas()
        self.lbl_total.lbl_valor.setText(str(stats['total']))
        self.lbl_pendientes.lbl_valor.setText(str(stats['pendientes']))
        self.lbl_urgentes.lbl_valor.setText(str(stats['urgentes']))

    def verificar_pagos(self):
        """Ejecuta la verificación de pagos vencidos."""
        try:
            cantidad = self.model.verificar_pagos_vencidos()
            QMessageBox.information(
                self,
                "Verificación Completa",
                f"Se crearon {cantidad} nuevas notificaciones de pagos vencidos."
            )
            self.cargar_notificaciones()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al verificar pagos: {str(e)}")

    def limpiar_antiguas(self):
        """Limpia notificaciones antiguas."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar notificaciones leídas con más de 30 días?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            cantidad = self.model.limpiar_notificaciones_antiguas()
            QMessageBox.information(
                self,
                "Limpieza Completa",
                f"Se eliminaron {cantidad} notificaciones antiguas."
            )
            self.cargar_notificaciones()

    def marcar_leida(self):
        """Marca la notificación seleccionada como leída."""
        fila = self.tabla.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Error", "Seleccioná una notificación.")
            return
        
        notif_id = int(self.tabla.item(fila, 0).text())
        self.model.marcar_como_leida(notif_id)
        self.cargar_notificaciones()

    def marcar_todas_leidas(self):
        """Marca todas las notificaciones como leídas."""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Marcar todas las notificaciones como leídas?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            notificaciones = self.model.obtener_notificaciones_pendientes()
            for notif in notificaciones:
                self.model.marcar_como_leida(notif[0])
            
            self.cargar_notificaciones()
            QMessageBox.information(
                self,
                "Completado",
                "Todas las notificaciones fueron marcadas como leídas."
            )

    def closeEvent(self, event):
        """Detiene el timer al cerrar."""
        self.timer.stop()
        event.accept()