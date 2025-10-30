'''from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sqlite3
from collections import Counter
import datetime


class StatsView(QWidget):
    def __init__(self, db_path="gym.db"):
        super().__init__()
        self.db_path = db_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("📊 Estadísticas del Gimnasio")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        # Gráfico 1: socios por plan
        self.canvas_planes = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(QLabel("Socios por Plan"))
        layout.addWidget(self.canvas_planes)

        # Gráfico 2: socios por mes
        self.canvas_meses = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(QLabel("Altas de Socios por Mes"))
        layout.addWidget(self.canvas_meses)

        self.setLayout(layout)
        self.actualizar_graficos()

    def actualizar_graficos(self):
        # --- Gráfico 1: socios por plan ---
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT p.nombre, COUNT(s.id)
            FROM socios s
            LEFT JOIN planes p ON s.plan_id = p.id
            GROUP BY p.nombre
        """)
        datos = c.fetchall()
        conn.close()

        nombres = [d[0] if d[0] else "Sin Plan" for d in datos]
        cantidades = [d[1] for d in datos]

        ax1 = self.canvas_planes.figure.subplots()
        ax1.clear()
        ax1.bar(nombres, cantidades)
        ax1.set_title("Socios por Plan")
        ax1.set_xlabel("Planes")
        ax1.set_ylabel("Cantidad")
        ax1.tick_params(axis="x", rotation=20)
        self.canvas_planes.draw()

        # --- Gráfico 2: socios por mes ---
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT fecha_alta FROM socios")
        fechas = [row[0] for row in c.fetchall()]
        conn.close()

        meses = [datetime.datetime.strptime(f, "%Y-%m-%d").strftime("%b") for f in fechas if f]
        conteo = Counter(meses)

        ax2 = self.canvas_meses.figure.subplots()
        ax2.clear()
        ax2.bar(conteo.keys(), conteo.values(), color="#5dade2")
        ax2.set_title("Altas de Socios por Mes")
        ax2.set_xlabel("Mes")
        ax2.set_ylabel("Cantidad")
        self.canvas_meses.draw()
'''
"""
views/stats.py
Vista de estadísticas con gráficos para el gimnasio.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sqlite3
from collections import Counter
import datetime


class StatsView(QWidget):
    def __init__(self, db_path="gimnasio.db"):
        super().__init__()
        self.db_path = db_path
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("📊 Estadísticas del Gimnasio")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        try:
            # Gráfico 1: socios por plan
            self.canvas_planes = FigureCanvas(Figure(figsize=(5, 3)))
            layout.addWidget(QLabel("Socios por Plan"))
            layout.addWidget(self.canvas_planes)

            # Gráfico 2: socios por mes
            self.canvas_meses = FigureCanvas(Figure(figsize=(5, 3)))
            layout.addWidget(QLabel("Inscripciones por Mes"))
            layout.addWidget(self.canvas_meses)

            self.setLayout(layout)
            self.actualizar_graficos()
        except ImportError:
            error_label = QLabel("⚠️ Para ver gráficos, instalá matplotlib:\npip install matplotlib")
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
            layout.addWidget(error_label)
            self.setLayout(layout)

    def actualizar_graficos(self):
        """Actualiza los gráficos con datos de la base de datos."""
        try:
            # --- Gráfico 1: socios por plan ---
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""
                SELECT p.nombre, COUNT(s.id)
                FROM socios s
                LEFT JOIN planes p ON s.plan_id = p.id
                GROUP BY p.nombre
            """)
            datos = c.fetchall()

            if datos:
                nombres = [d[0] if d[0] else "Sin Plan" for d in datos]
                cantidades = [d[1] for d in datos]

                ax1 = self.canvas_planes.figure.subplots()
                ax1.clear()
                ax1.bar(nombres, cantidades, color='#2196F3')
                ax1.set_title("Socios por Plan")
                ax1.set_xlabel("Planes")
                ax1.set_ylabel("Cantidad")
                ax1.tick_params(axis="x", rotation=20)
                self.canvas_planes.draw()

            # --- Gráfico 2: socios por mes ---
            c.execute("SELECT fecha_inscripcion FROM socios WHERE fecha_inscripcion IS NOT NULL")
            fechas = [row[0] for row in c.fetchall()]
            conn.close()

            if fechas:
                meses = []
                for f in fechas:
                    try:
                        mes = datetime.datetime.strptime(f, "%Y-%m-%d").strftime("%b")
                        meses.append(mes)
                    except:
                        pass
                
                conteo = Counter(meses)

                ax2 = self.canvas_meses.figure.subplots()
                ax2.clear()
                ax2.bar(conteo.keys(), conteo.values(), color="#5dade2")
                ax2.set_title("Inscripciones por Mes")
                ax2.set_xlabel("Mes")
                ax2.set_ylabel("Cantidad")
                self.canvas_meses.draw()

        except Exception as e:
            print(f"Error al actualizar gráficos: {e}")