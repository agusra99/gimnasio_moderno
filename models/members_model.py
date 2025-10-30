import sqlite3

class MembersModel:
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

    def agregar(self, nombre, apellido, telefono, fecha_alta, plan_id=None):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO socios (nombre, apellido, telefono, fecha_alta, plan_id)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, apellido, telefono, fecha_alta, plan_id))
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
        rows = c.fetchall()
        conn.close()
        return rows

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
