
"""
views/dashboard_home.py
Dashboard principal completo con gráficos, alertas y resumen visual mejorado.
Se muestra al iniciar la aplicación.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame,
    QScrollArea, QGroupBox, QPushButton, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
import sqlite3
from datetime import datetime, timedelta
from collections import Counter, defaultdict

# Intentar importar matplotlib
try:
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import matplotlib
    matplotlib.use('Qt5Agg')
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class DashboardHome(QWidget):
    def __init__(self, db_path, notifications_model=None):
        super().__init__()
        self.db_path = db_path
        self.notifications_model = notifications_model
        self.init_ui()
        
        # Auto-actualizar cada 60 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_todo)
        self.timer.start(60000)

    def init_ui(self):
        # Crear scroll area para todo el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Widget principal dentro del scroll
        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)

        # === ENCABEZADO ===
        header_layout = QHBoxLayout()
        
        title = QLabel("📊 Sistema de Gestión de Gimnasio")
        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #0078d7;
            padding: 15px;
            background-color: transparent;
        """)
        
        fecha_label = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M"))
        fecha_label.setStyleSheet("font-size: 14px; color: #666; padding: 15px;")
        
        btn_actualizar = QPushButton("🔄 Actualizar")
        btn_actualizar.setStyleSheet("""
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
        btn_actualizar.clicked.connect(self.actualizar_todo)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(fecha_label)
        header_layout.addWidget(btn_actualizar)
        layout.addLayout(header_layout)

        # === TARJETAS DE RESUMEN ===
        cards_layout = QHBoxLayout()
        
        self.card_socios = self._crear_card("👥", "Socios Totales", "0", "#2196F3")
        self.card_activos = self._crear_card("✅", "Activos (30 días)", "0", "#4CAF50")
        self.card_vencidos = self._crear_card("⚠️", "Pagos Vencidos", "0", "#F44336")
        self.card_ingresos = self._crear_card("💰", "Ingresos del Mes", "$0", "#FF9800")
        
        cards_layout.addWidget(self.card_socios)
        cards_layout.addWidget(self.card_activos)
        cards_layout.addWidget(self.card_vencidos)
        cards_layout.addWidget(self.card_ingresos)
        
        layout.addLayout(cards_layout)

        # === ALERTAS URGENTES ===
        alertas_group = QGroupBox("🚨 Alertas Urgentes")
        alertas_group.setObjectName("alertasGroup")
        alertas_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 3px solid #F44336;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
                background: white;
            }
            /* Regla específica por id para forzar color incluso si hay un stylesheet global */
            QGroupBox#alertasGroup::title {
                color: #000000; /* Título en negro */
                padding: 5px;
            }
            QGroupBox::title {
                color: #000000; /* Fallback */
                padding: 5px;
            }
        """)
        alertas_layout = QVBoxLayout()
        
        self.tabla_alertas = QTableWidget()
        self.tabla_alertas.setColumnCount(4)
        self.tabla_alertas.setHorizontalHeaderLabels([
            "Socio", "Problema", "Días Vencido", "Último Pago"
        ])
        # Configurar ancho de columnas
        self.tabla_alertas.setColumnWidth(0, 200)  # Socio
        self.tabla_alertas.setColumnWidth(1, 250)  # Problema
        self.tabla_alertas.setColumnWidth(2, 150)  # Días Vencido
        self.tabla_alertas.horizontalHeader().setStretchLastSection(True)
        self.tabla_alertas.setMaximumHeight(180)
        self.tabla_alertas.setMinimumHeight(180)
        self.tabla_alertas.verticalHeader().setVisible(False)
        self.tabla_alertas.setAlternatingRowColors(True)
        self.tabla_alertas.setStyleSheet("""
            QTableWidget {
                background-color: #ffebee;
                border: none;
                gridline-color: #ffcdd2;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #F44336;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
        """)
        
        alertas_layout.addWidget(self.tabla_alertas)
        alertas_group.setLayout(alertas_layout)
        layout.addWidget(alertas_group)

        # === PRÓXIMOS VENCIMIENTOS ===
        proximos_group = QGroupBox("⏰ Próximos Vencimientos (5 días)")
        proximos_group.setObjectName("proximosGroup")
        proximos_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 3px solid #FF9800;
                border-radius: 10px;
                margin-top: 10px;
                padding: 15px;
                background: white;
            }
            QGroupBox::title {
                color: #FF9800;
                padding: 5px;
            }
        """)
        proximos_layout = QVBoxLayout()

        self.tabla_proximos = QTableWidget()
        self.tabla_proximos.setColumnCount(4)
        self.tabla_proximos.setHorizontalHeaderLabels([
            "Socio", "Teléfono", "Último Pago", "Vence en"
        ])
        # Configurar ancho de columnas
        self.tabla_proximos.setColumnWidth(0, 200)  # Socio
        self.tabla_proximos.setColumnWidth(1, 150)  # Teléfono
        self.tabla_proximos.setColumnWidth(2, 150)  # Último Pago
        self.tabla_proximos.horizontalHeader().setStretchLastSection(True)
        self.tabla_proximos.setMaximumHeight(180)
        self.tabla_proximos.setMinimumHeight(180)
        self.tabla_proximos.verticalHeader().setVisible(False)
        self.tabla_proximos.setAlternatingRowColors(True)
        self.tabla_proximos.setStyleSheet("""
            QTableWidget {
                background-color: #fff3e0;
                border: none;
                gridline-color: #ffe0b2;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #FF9800;
                color: white;
                padding: 10px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
        """)

        proximos_layout.addWidget(self.tabla_proximos)
        proximos_group.setLayout(proximos_layout)
        layout.addWidget(proximos_group)

        # === GRÁFICOS ===
        if MATPLOTLIB_AVAILABLE:
            # Primera fila de gráficos
            graficos_layout1 = QHBoxLayout()
            
            # Gráfico 1: Inscripciones por mes
            grafico1_group = QGroupBox("📈 Inscripciones por Mes (Último Año)")
            grafico1_layout = QVBoxLayout()
            
            self.fig_inscripciones = Figure(figsize=(7, 4), facecolor='white')
            self.canvas_inscripciones = FigureCanvas(self.fig_inscripciones)
            self.canvas_inscripciones.setMinimumHeight(300)
            
            grafico1_layout.addWidget(self.canvas_inscripciones)
            grafico1_group.setLayout(grafico1_layout)
            grafico1_group.setStyleSheet(self._get_groupbox_style("#2196F3"))
            
            # Gráfico 2: Socios por plan (torta)
            grafico2_group = QGroupBox("📊 Distribución por Plan")
            grafico2_layout = QVBoxLayout()
            
            self.fig_planes = Figure(figsize=(7, 4), facecolor='white')
            self.canvas_planes = FigureCanvas(self.fig_planes)
            self.canvas_planes.setMinimumHeight(300)
            
            grafico2_layout.addWidget(self.canvas_planes)
            grafico2_group.setLayout(grafico2_layout)
            grafico2_group.setStyleSheet(self._get_groupbox_style("#4CAF50"))
            
            graficos_layout1.addWidget(grafico1_group)
            graficos_layout1.addWidget(grafico2_group)
            layout.addLayout(graficos_layout1)
            
            # Segunda fila de gráficos
            graficos_layout2 = QHBoxLayout()
            
            # Gráfico 3: Ingresos por mes
            grafico3_group = QGroupBox("💰 Ingresos Mensuales (Último Semestre)")
            grafico3_layout = QVBoxLayout()
            
            self.fig_ingresos = Figure(figsize=(7, 4), facecolor='white')
            self.canvas_ingresos = FigureCanvas(self.fig_ingresos)
            self.canvas_ingresos.setMinimumHeight(300)
            
            grafico3_layout.addWidget(self.canvas_ingresos)
            grafico3_group.setLayout(grafico3_layout)
            grafico3_group.setStyleSheet(self._get_groupbox_style("#FF9800"))
            
            # Gráfico 4: Estado de pagos (torta)
            grafico4_group = QGroupBox("📋 Estado de Socios")
            grafico4_layout = QVBoxLayout()
            
            self.fig_estado = Figure(figsize=(7, 4), facecolor='white')
            self.canvas_estado = FigureCanvas(self.fig_estado)
            self.canvas_estado.setMinimumHeight(300)
            
            grafico4_layout.addWidget(self.canvas_estado)
            grafico4_group.setLayout(grafico4_layout)
            grafico4_group.setStyleSheet(self._get_groupbox_style("#9C27B0"))
            
            graficos_layout2.addWidget(grafico3_group)
            graficos_layout2.addWidget(grafico4_group)
            layout.addLayout(graficos_layout2)
        else:
            # Mensaje si matplotlib no está instalado
            warning = self._crear_warning_matplotlib()
            layout.addWidget(warning)

        scroll.setWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        # Cargar datos iniciales
        self.actualizar_todo()

    def _crear_card(self, icono, titulo, valor, color):
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
        
        lbl_icono = QLabel(icono)
        lbl_icono.setStyleSheet("font-size: 42px;")
        lbl_icono.setAlignment(Qt.AlignCenter)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 13px; color: #666; font-weight: 500;")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setStyleSheet(f"font-size: 32px; font-weight: bold; color: {color};")
        lbl_valor.setAlignment(Qt.AlignCenter)
        
        frame_layout.addWidget(lbl_icono)
        frame_layout.addWidget(lbl_titulo)
        frame_layout.addWidget(lbl_valor)
        
        frame.lbl_valor = lbl_valor
        return frame

    def _get_groupbox_style(self, color):
        """Retorna el estilo para un groupbox."""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                border: 2px solid {color};
                border-radius: 10px;
                margin-top: 15px;
                padding: 15px;
                background: white;
            }}
            QGroupBox::title {{
                color: {color};
                padding: 5px;
            }}
        """

    def _crear_warning_matplotlib(self):
        """Crea un mensaje de advertencia si matplotlib no está instalado."""
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 3px solid #ffc107;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        warning_layout = QVBoxLayout(warning_frame)
        
        icon_label = QLabel("📊")
        icon_label.setStyleSheet("font-size: 64px;")
        icon_label.setAlignment(Qt.AlignCenter)
        
        warning_label = QLabel("⚠️ Gráficos no disponibles")
        warning_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #856404;")
        warning_label.setAlignment(Qt.AlignCenter)
        
        install_label = QLabel(
            "Para ver los gráficos estadísticos, instalá matplotlib:\n\n"
            "pip install matplotlib"
        )
        install_label.setStyleSheet("font-size: 14px; color: #856404;")
        install_label.setAlignment(Qt.AlignCenter)
        
        warning_layout.addWidget(icon_label)
        warning_layout.addWidget(warning_label)
        warning_layout.addWidget(install_label)
        
        return warning_frame

    def _get_bold_font(self):
        """Retorna una fuente en negrita."""
        font = QFont()
        font.setBold(True)
        return font

    def actualizar_todo(self):
        """Actualiza todos los datos del dashboard."""
        self.actualizar_estadisticas()
        self.actualizar_alertas()
        self.actualizar_proximos_vencimientos()
        if MATPLOTLIB_AVAILABLE:
            self.actualizar_graficos()

    def actualizar_estadisticas(self):
        """Actualiza las tarjetas de estadísticas."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Total de socios
            c.execute("SELECT COUNT(*) FROM socios")
            total_socios = c.fetchone()[0]
            self.card_socios.lbl_valor.setText(str(total_socios))

            # Socios activos (con pago en últimos 30 días)
            hace_30_dias = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            c.execute("""
                SELECT COUNT(DISTINCT socio_id) FROM pagos
                WHERE fecha_pago >= ?
            """, (hace_30_dias,))
            activos = c.fetchone()[0]
            self.card_activos.lbl_valor.setText(str(activos))

            # Ingresos del mes actual
            mes_actual = datetime.now().strftime('%Y-%m')
            c.execute("""
                SELECT COALESCE(SUM(monto), 0) FROM pagos
                WHERE fecha_pago LIKE ?
            """, (f"{mes_actual}%",))
            ingresos = c.fetchone()[0]
            self.card_ingresos.lbl_valor.setText(f"${ingresos:,.0f}")

            # Contar pagos vencidos
            c.execute("""
                SELECT COUNT(*) FROM (
                    SELECT s.id
                    FROM socios s
                    LEFT JOIN pagos p ON s.id = p.socio_id
                    LEFT JOIN planes pl ON s.plan_id = pl.id
                    GROUP BY s.id
                    HAVING MAX(p.fecha_pago) IS NULL 
                    OR julianday('now') - julianday(MAX(p.fecha_pago)) > COALESCE(pl.duracion_dias, 30)
                )
            """)
            vencidos = c.fetchone()[0]
            self.card_vencidos.lbl_valor.setText(str(vencidos))

            conn.close()
        except Exception as e:
            print(f"Error al actualizar estadísticas: {e}")

    def actualizar_alertas(self):
        """Actualiza la tabla de alertas urgentes."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT s.nombre || ' ' || s.apellido, 
                       MAX(p.fecha_pago) as ultimo_pago,
                       COALESCE(pl.duracion_dias, 30) as duracion,
                       s.telefono
                FROM socios s
                LEFT JOIN pagos p ON s.id = p.socio_id
                LEFT JOIN planes pl ON s.plan_id = pl.id
                GROUP BY s.id
            """)
            
            socios_data = c.fetchall()
            vencidos = []
            
            for socio in socios_data:
                nombre, ultimo_pago, duracion, telefono = socio
                
                if ultimo_pago:
                    fecha_ultimo = datetime.strptime(ultimo_pago, '%Y-%m-%d')
                    dias_transcurridos = (datetime.now() - fecha_ultimo).days
                    
                    if dias_transcurridos > duracion:
                        dias_vencidos = dias_transcurridos - duracion
                        vencidos.append((nombre, dias_vencidos, ultimo_pago, telefono))
                else:
                    vencidos.append((nombre, "Sin pagos", "Nunca", telefono or "Sin tel."))
            
            # Ordenar por días vencidos (mayor a menor)
            vencidos_ordenados = sorted([v for v in vencidos if isinstance(v[1], int)], 
                                       key=lambda x: x[1], reverse=True)
            sin_pagos = [v for v in vencidos if not isinstance(v[1], int)]
            vencidos = vencidos_ordenados + sin_pagos
            
            # Mostrar top 10 o mensaje si no hay datos
            if len(vencidos) == 0:
                self.tabla_alertas.setRowCount(1)
                item_vacio = QTableWidgetItem("✓ No hay alertas urgentes en este momento")
                item_vacio.setTextAlignment(Qt.AlignCenter)
                item_vacio.setForeground(QColor(76, 175, 80))
                self.tabla_alertas.setSpan(0, 0, 1, 4)
                self.tabla_alertas.setItem(0, 0, item_vacio)
                # Forzar texto negro en la celda vacía solo si no estamos en tema oscuro
                try:
                    from PySide6.QtWidgets import QApplication
                    global_ss = QApplication.instance().styleSheet() if QApplication.instance() else ""
                except Exception:
                    global_ss = ""
                is_dark = ('Tema Oscuro' in global_ss) or ('background-color: #1e1e1e' in global_ss)
                it0 = self.tabla_alertas.item(0, 0)
                if it0 and not is_dark:
                    it0.setForeground(QColor(0, 0, 0))
            else:
                self.tabla_alertas.clearSpans()
                self.tabla_alertas.setRowCount(min(len(vencidos), 10))
                for row, (nombre, dias, fecha, tel) in enumerate(vencidos[:10]):
                    # Socio
                    item_nombre = QTableWidgetItem(nombre)
                    item_nombre.setFont(self._get_bold_font())
                    self.tabla_alertas.setItem(row, 0, item_nombre)
                    
                    # Problema
                    problema = f"Pago vencido" if isinstance(dias, int) else "Sin pagos registrados"
                    self.tabla_alertas.setItem(row, 1, QTableWidgetItem(problema))
                    
                    # Días vencido
                    dias_texto = f"{dias} días" if isinstance(dias, int) else dias
                    item_dias = QTableWidgetItem(dias_texto)
                    item_dias.setForeground(QColor(211, 47, 47))
                    item_dias.setBackground(QColor(255, 235, 238))
                    item_dias.setFont(self._get_bold_font())
                    item_dias.setTextAlignment(Qt.AlignCenter)
                    self.tabla_alertas.setItem(row, 2, item_dias)
                    
                    # Último pago
                    self.tabla_alertas.setItem(row, 3, QTableWidgetItem(fecha))

                # Forzar texto negro en todas las celdas de la tabla de alertas solo si no estamos en tema oscuro.
                try:
                    from PySide6.QtWidgets import QApplication
                    global_ss = QApplication.instance().styleSheet() if QApplication.instance() else ""
                except Exception:
                    global_ss = ""

                is_dark = ('Tema Oscuro' in global_ss) or ('background-color: #1e1e1e' in global_ss)
                if not is_dark:
                    for r in range(self.tabla_alertas.rowCount()):
                        for c in range(self.tabla_alertas.columnCount()):
                            it = self.tabla_alertas.item(r, c)
                            if it:
                                it.setForeground(QColor(0, 0, 0))
            
            conn.close()
        except Exception as e:
            print(f"Error al actualizar alertas: {e}")
            # Mostrar mensaje de error en la tabla
            self.tabla_alertas.setRowCount(1)
            item_error = QTableWidgetItem(f"⚠️ Error al cargar alertas: {str(e)}")
            item_error.setTextAlignment(Qt.AlignCenter)
            item_error.setForeground(QColor(244, 67, 54))
            self.tabla_alertas.setSpan(0, 0, 1, 4)
            self.tabla_alertas.setItem(0, 0, item_error)
            # Forzar texto negro también para el mensaje de error solo si no estamos en tema oscuro
            try:
                from PySide6.QtWidgets import QApplication
                global_ss = QApplication.instance().styleSheet() if QApplication.instance() else ""
            except Exception:
                global_ss = ""
            is_dark_err = ('Tema Oscuro' in global_ss) or ('background-color: #1e1e1e' in global_ss)
            it_err = self.tabla_alertas.item(0, 0)
            if it_err and not is_dark_err:
                it_err.setForeground(QColor(0, 0, 0))

    def actualizar_proximos_vencimientos(self):
        """Actualiza la tabla de próximos vencimientos."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute("""
                SELECT s.nombre || ' ' || s.apellido, 
                       s.telefono,
                       MAX(p.fecha_pago) as ultimo_pago,
                       COALESCE(pl.duracion_dias, 30) as duracion
                FROM socios s
                LEFT JOIN pagos p ON s.id = p.socio_id
                LEFT JOIN planes pl ON s.plan_id = pl.id
                GROUP BY s.id
            """)
            
            socios_data = c.fetchall()
            proximos = []
            
            for socio in socios_data:
                nombre, telefono, ultimo_pago, duracion = socio
                
                if ultimo_pago:
                    fecha_ultimo = datetime.strptime(ultimo_pago, '%Y-%m-%d')
                    dias_transcurridos = (datetime.now() - fecha_ultimo).days
                    
                    # Próximos a vencer (entre 0 y 5 días antes del vencimiento)
                    if duracion - 5 <= dias_transcurridos <= duracion:
                        dias_restantes = duracion - dias_transcurridos
                        proximos.append((nombre, telefono or "Sin tel.", ultimo_pago, dias_restantes))
            
            # Ordenar por días restantes (menor a mayor)
            proximos = sorted(proximos, key=lambda x: x[3])
            
            # Mostrar datos o mensaje si no hay
            if len(proximos) == 0:
                self.tabla_proximos.setRowCount(1)
                item_vacio = QTableWidgetItem("✓ No hay vencimientos próximos en los siguientes 5 días")
                item_vacio.setTextAlignment(Qt.AlignCenter)
                item_vacio.setForeground(QColor(76, 175, 80))
                self.tabla_proximos.setSpan(0, 0, 1, 4)
                self.tabla_proximos.setItem(0, 0, item_vacio)
            else:
                self.tabla_proximos.clearSpans()
                self.tabla_proximos.setRowCount(len(proximos))
                for row, (nombre, tel, fecha, dias) in enumerate(proximos):
                    # Socio
                    item_nombre = QTableWidgetItem(nombre)
                    item_nombre.setFont(self._get_bold_font())
                    self.tabla_proximos.setItem(row, 0, item_nombre)
                    
                    # Teléfono
                    self.tabla_proximos.setItem(row, 1, QTableWidgetItem(tel))
                    
                    # Último pago
                    self.tabla_proximos.setItem(row, 2, QTableWidgetItem(fecha))
                    
                    # Días restantes
                    dias_texto = f"{dias} días"
                    item_dias = QTableWidgetItem(dias_texto)
                    item_dias.setForeground(QColor(245, 124, 0))
                    item_dias.setBackground(QColor(255, 243, 224))
                    item_dias.setFont(self._get_bold_font())
                    item_dias.setTextAlignment(Qt.AlignCenter)
                    self.tabla_proximos.setItem(row, 3, item_dias)
            
            conn.close()
        except Exception as e:
            print(f"Error al actualizar próximos vencimientos: {e}")
            # Mostrar mensaje de error en la tabla
            self.tabla_proximos.setRowCount(1)
            item_error = QTableWidgetItem(f"⚠️ Error al cargar vencimientos: {str(e)}")
            item_error.setTextAlignment(Qt.AlignCenter)
            item_error.setForeground(QColor(244, 67, 54))
            self.tabla_proximos.setSpan(0, 0, 1, 4)
            self.tabla_proximos.setItem(0, 0, item_error)

    def actualizar_graficos(self):
        """Actualiza todos los gráficos."""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # === GRÁFICO 1: Inscripciones por mes ===
            c.execute("""
                SELECT fecha_inscripcion FROM socios 
                WHERE fecha_inscripcion IS NOT NULL
                AND fecha_inscripcion >= date('now', '-12 months')
            """)
            fechas = [row[0] for row in c.fetchall()]
            
            if fechas:
                meses_dict = defaultdict(int)
                for f in fechas:
                    try:
                        mes_anio = datetime.strptime(f, "%Y-%m-%d").strftime("%b %Y")
                        meses_dict[mes_anio] += 1
                    except:
                        pass
                
                if meses_dict:
                    self.fig_inscripciones.clear()
                    ax1 = self.fig_inscripciones.add_subplot(111)
                    ax1.bar(list(meses_dict.keys()), list(meses_dict.values()), color='#2196F3', alpha=0.8)
                    ax1.set_title("Inscripciones por Mes", fontsize=14, fontweight='bold', pad=20)
                    ax1.set_xlabel("Mes", fontsize=11)
                    ax1.set_ylabel("Cantidad", fontsize=11)
                    ax1.tick_params(axis='x', rotation=45, labelsize=9)
                    ax1.grid(axis='y', alpha=0.3)
                    self.fig_inscripciones.tight_layout()
                    self.canvas_inscripciones.draw()
            
            # === GRÁFICO 2: Socios por plan (torta) ===
            c.execute("""
                SELECT COALESCE(p.nombre, 'Sin Plan'), COUNT(s.id)
                FROM socios s
                LEFT JOIN planes p ON s.plan_id = p.id
                GROUP BY p.nombre
            """)
            datos_planes = c.fetchall()
            
            if datos_planes:
                self.fig_planes.clear()
                ax2 = self.fig_planes.add_subplot(111)
                nombres = [d[0] for d in datos_planes]
                cantidades = [d[1] for d in datos_planes]
                colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
                ax2.pie(cantidades, labels=nombres, autopct='%1.1f%%', 
                       colors=colors[:len(nombres)], startangle=90, textprops={'fontsize': 10})
                ax2.set_title("Distribución por Plan", fontsize=14, fontweight='bold', pad=20)
                self.fig_planes.tight_layout()
                self.canvas_planes.draw()
            
            # === GRÁFICO 3: Ingresos mensuales ===
            c.execute("""
                SELECT strftime('%Y-%m', fecha_pago) as mes, SUM(monto)
                FROM pagos
                WHERE fecha_pago >= date('now', '-6 months')
                GROUP BY mes
                ORDER BY mes
            """)
            datos_ingresos = c.fetchall()
            
            if datos_ingresos:
                self.fig_ingresos.clear()
                ax3 = self.fig_ingresos.add_subplot(111)
                meses = [datetime.strptime(d[0], "%Y-%m").strftime("%b %Y") for d in datos_ingresos]
                montos = [d[1] for d in datos_ingresos]
                ax3.plot(meses, montos, marker='o', color='#FF9800', linewidth=2, markersize=8)
                ax3.fill_between(range(len(meses)), montos, alpha=0.3, color='#FF9800')
                ax3.set_title("Ingresos Mensuales", fontsize=14, fontweight='bold', pad=20)
                ax3.set_xlabel("Mes", fontsize=11)
                ax3.set_ylabel("Ingresos ($)", fontsize=11)
                ax3.tick_params(axis='x', rotation=45, labelsize=9)
                ax3.grid(True, alpha=0.3)
                self.fig_ingresos.tight_layout()
                self.canvas_ingresos.draw()
            
            # === GRÁFICO 4: Estado de socios (torta) ===
            hace_30_dias = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            c.execute("""
                SELECT COUNT(DISTINCT socio_id) FROM pagos
                WHERE fecha_pago >= ?
            """, (hace_30_dias,))
            activos = c.fetchone()[0]
            
            c.execute("SELECT COUNT(*) FROM socios")
            total = c.fetchone()[0]
            inactivos = total - activos
            
            if total > 0:
                self.fig_estado.clear()
                ax4 = self.fig_estado.add_subplot(111)
                labels = ['Activos\n(últimos 30 días)', 'Inactivos']
                sizes = [activos, inactivos]
                colors = ['#4CAF50', '#F44336']
                ax4.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, 
                       startangle=90, textprops={'fontsize': 10})
                ax4.set_title("Estado de Socios", fontsize=14, fontweight='bold', pad=20)
                self.fig_estado.tight_layout()
                self.canvas_estado.draw()
            
            conn.close()
        except Exception as e:
            print(f"Error al actualizar gráficos: {e}")

    def closeEvent(self, event):
        """Detiene el timer al cerrar."""
        if hasattr(self, 'timer'):
            self.timer.stop()
        event.accept()