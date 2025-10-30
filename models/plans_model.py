"""
models/plans_model.py
Modelo para la gestión de planes del gimnasio.
"""

import sqlite3


class PlansModel:
    def __init__(self, db_path):
        self.db_path = db_path
        self.crear_tabla()

    def conectar(self):
        return sqlite3.connect(self.db_path)

    def crear_tabla(self):
        conn = self.conectar()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS planes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                duracion_dias INTEGER NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def agregar_plan(self, nombre, precio, duracion_dias):
        conn = self.conectar()
        c = conn.cursor()
        c.execute("INSERT INTO planes (nombre, precio, duracion_dias) VALUES (?, ?, ?)",
                  (nombre, precio, duracion_dias))
        conn.commit()
        conn.close()

    def obtener_planes(self):
        conn = self.conectar()
        c = conn.cursor()
        c.execute("SELECT id, nombre, precio, duracion_dias FROM planes")
        data = c.fetchall()
        conn.close()
        return data

    def eliminar_plan(self, plan_id):
        conn = self.conectar()
        c = conn.cursor()
        c.execute("DELETE FROM planes WHERE id = ?", (plan_id,))
        conn.commit()
        conn.close()

    def actualizar_plan(self, plan_id, nombre, precio, duracion_dias):
        conn = self.conectar()
        c = conn.cursor()
        c.execute("""
            UPDATE planes 
            SET nombre = ?, precio = ?, duracion_dias = ? 
            WHERE id = ?
        """, (nombre, precio, duracion_dias, plan_id))
        conn.commit()
        conn.close()
