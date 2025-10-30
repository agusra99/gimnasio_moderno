'''import sqlite3

class MembersController:
    def __init__(self, db_path="gym.db"):
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS socios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                fecha_alta TEXT,
                plan_id INTEGER,
                FOREIGN KEY(plan_id) REFERENCES planes(id)
            )
        """)
        conn.commit()
        conn.close()

    def obtener_todos(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT s.id, s.nombre, s.apellido, s.telefono, s.fecha_alta,
                   p.nombre AS plan
            FROM socios s
            LEFT JOIN planes p ON s.plan_id = p.id
            ORDER BY s.id DESC
        """)
        socios = c.fetchall()
        conn.close()
        return socios

    def obtener_planes(self):
        """Obtiene los planes disponibles para el combo de selección."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM planes ORDER BY nombre ASC")
        planes = c.fetchall()
        conn.close()
        return planes

    def agregar(self, nombre, apellido, telefono, fecha_alta, plan_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO socios (nombre, apellido, telefono, fecha_alta, plan_id)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, apellido, telefono, fecha_alta, plan_id))
        conn.commit()
        conn.close()

    def actualizar(self, socio_id, nombre, apellido, telefono, plan_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE socios
            SET nombre=?, apellido=?, telefono=?, plan_id=?
            WHERE id=?
        """, (nombre, apellido, telefono, plan_id, socio_id))
        conn.commit()
        conn.close()

    def eliminar(self, socio_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM socios WHERE id=?", (socio_id,))
        conn.commit()
        conn.close()
'''
"""
controllers/members_controller.py
Controlador para la gestión de socios.
"""

import sqlite3


class MembersController:
    def __init__(self, db_path="gimnasio.db"):
        self.db_path = db_path
        self.create_table()

    def create_table(self):
        """Crea la tabla de socios si no existe."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS socios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                fecha_inscripcion TEXT,
                plan_id INTEGER,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY(plan_id) REFERENCES planes(id)
            )
        """)
        conn.commit()
        conn.close()

    def obtener_todos(self):
        """Obtiene todos los socios con información del plan."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            SELECT s.id, s.nombre, s.apellido, s.telefono, s.fecha_inscripcion,
                   p.nombre AS plan
            FROM socios s
            LEFT JOIN planes p ON s.plan_id = p.id
            ORDER BY s.id DESC
        """)
        socios = c.fetchall()
        conn.close()
        return socios

    def obtener_planes(self):
        """Obtiene los planes disponibles para el combo de selección."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT id, nombre FROM planes ORDER BY nombre ASC")
        planes = c.fetchall()
        conn.close()
        return planes

    def agregar(self, nombre, apellido, telefono, fecha_inscripcion, plan_id):
        """Agrega un nuevo socio."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO socios (nombre, apellido, telefono, fecha_inscripcion, plan_id, activo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (nombre, apellido, telefono, fecha_inscripcion, plan_id))
        conn.commit()
        conn.close()

    def actualizar(self, socio_id, nombre, apellido, telefono, plan_id):
        """Actualiza los datos de un socio existente."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            UPDATE socios
            SET nombre=?, apellido=?, telefono=?, plan_id=?
            WHERE id=?
        """, (nombre, apellido, telefono, plan_id, socio_id))
        conn.commit()
        conn.close()

    def eliminar(self, socio_id):
        """Elimina un socio por ID."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("DELETE FROM socios WHERE id=?", (socio_id,))
        conn.commit()
        conn.close()

    def buscar(self, termino):
        """Busca socios por nombre, apellido o teléfono."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        termino = f"%{termino}%"
        c.execute("""
            SELECT s.id, s.nombre, s.apellido, s.telefono, s.fecha_inscripcion,
                   p.nombre AS plan
            FROM socios s
            LEFT JOIN planes p ON s.plan_id = p.id
            WHERE s.nombre LIKE ? OR s.apellido LIKE ? OR s.telefono LIKE ?
            ORDER BY s.id DESC
        """, (termino, termino, termino))
        socios = c.fetchall()
        conn.close()
        return socios