"""
connection.py
Módulo encargado de manejar la conexión a la base de datos SQLite.
Incluye creación automática del archivo `gimnasio.db` y las tablas principales.
"""
import sqlite3


class DatabaseConnection:
    def __init__(self, db_name: str = "gimnasio.db"):
        self.db_name = db_name
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_name)
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")

    def create_tables(self):
        cursor = self.conn.cursor()

        # Tabla de socios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS socios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                fecha_inscripcion TEXT NOT NULL,
                plan TEXT,
                activo INTEGER DEFAULT 1
            )
        ''')

        # Tabla de pagos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                socio_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                fecha_pago TEXT NOT NULL,
                mes_correspondiente TEXT NOT NULL,
                FOREIGN KEY(socio_id) REFERENCES socios(id)
            )
        ''')

        # Tabla de notificaciones o alertas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alertas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                socio_id INTEGER NOT NULL,
                mensaje TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                leida INTEGER DEFAULT 0,
                FOREIGN KEY(socio_id) REFERENCES socios(id)
            )
        ''')

        self.conn.commit()

    def execute(self, query: str, params: tuple = ()):  
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor

    def fetchall(self, query: str, params: tuple = ()):  
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()

    def fetchone(self, query: str, params: tuple = ()):  
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()

    def close(self):
        if self.conn:
            self.conn.close()
