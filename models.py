"""
models.py
Contiene las clases modelo para representar entidades del gimnasio: Socio, Pago y Alerta.
Cada clase incluye métodos básicos CRUD (crear, leer, actualizar, eliminar) conectados a la base de datos.
"""
from datetime import datetime


class Socio:
    def __init__(self, db_connection):
        self.db = db_connection

    def agregar(self, nombre, apellido, telefono, email, plan):
        fecha_inscripcion = datetime.now().strftime('%Y-%m-%d')
        query = '''INSERT INTO socios (nombre, apellido, telefono, email, fecha_inscripcion, plan, activo)
                   VALUES (?, ?, ?, ?, ?, ?, 1)'''
        self.db.execute(query, (nombre, apellido, telefono, email, fecha_inscripcion, plan))

    def obtener_todos(self):
        return self.db.fetchall("SELECT * FROM socios ORDER BY apellido ASC")

    def buscar_por_id(self, socio_id):
        return self.db.fetchone("SELECT * FROM socios WHERE id = ?", (socio_id,))

    def actualizar(self, socio_id, nombre, apellido, telefono, email, plan, activo=1):
        query = '''UPDATE socios SET nombre=?, apellido=?, telefono=?, email=?, plan=?, activo=? WHERE id=?'''
        self.db.execute(query, (nombre, apellido, telefono, email, plan, activo, socio_id))

    def eliminar(self, socio_id):
        self.db.execute("DELETE FROM socios WHERE id=?", (socio_id,))


class Pago:
    def __init__(self, db_connection):
        self.db = db_connection

    def registrar_pago(self, socio_id, monto, mes_correspondiente):
        fecha_pago = datetime.now().strftime('%Y-%m-%d')
        query = '''INSERT INTO pagos (socio_id, monto, fecha_pago, mes_correspondiente)
                   VALUES (?, ?, ?, ?)'''
        self.db.execute(query, (socio_id, monto, fecha_pago, mes_correspondiente))

    def obtener_pagos(self):
        return self.db.fetchall('''
            SELECT p.id, s.nombre || ' ' || s.apellido AS socio, p.monto, p.fecha_pago, p.mes_correspondiente
            FROM pagos p JOIN socios s ON p.socio_id = s.id
            ORDER BY p.fecha_pago DESC
        ''')

    def obtener_pagos_por_socio(self, socio_id):
        return self.db.fetchall("SELECT * FROM pagos WHERE socio_id=? ORDER BY fecha_pago DESC", (socio_id,))


class Alerta:
    def __init__(self, db_connection):
        self.db = db_connection

    def crear_alerta(self, socio_id, mensaje):
        fecha_creacion = datetime.now().strftime('%Y-%m-%d')
        query = '''INSERT INTO alertas (socio_id, mensaje, fecha_creacion, leida)
                   VALUES (?, ?, ?, 0)'''
        self.db.execute(query, (socio_id, mensaje, fecha_creacion))

    def obtener_no_leidas(self):
        return self.db.fetchall('''
            SELECT a.id, s.nombre || ' ' || s.apellido AS socio, a.mensaje, a.fecha_creacion
            FROM alertas a JOIN socios s ON a.socio_id = s.id
            WHERE a.leida = 0
            ORDER BY a.fecha_creacion DESC
        ''')

    def marcar_como_leida(self, alerta_id):
        self.db.execute("UPDATE alertas SET leida = 1 WHERE id=?", (alerta_id,))
