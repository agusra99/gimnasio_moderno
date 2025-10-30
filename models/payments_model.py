"""
models/payments_model.py
Modelo completo para la gestión de pagos de socios.
"""

import sqlite3
from datetime import datetime, timedelta


class PaymentsModel:
    def __init__(self, db_path):
        self.db_path = db_path
        self._verificar_tabla()

    def _verificar_tabla(self):
        """Verifica que la tabla de pagos exista."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                socio_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                fecha_pago TEXT NOT NULL,
                mes_correspondiente TEXT NOT NULL,
                metodo_pago TEXT DEFAULT 'efectivo',
                observaciones TEXT,
                FOREIGN KEY(socio_id) REFERENCES socios(id)
            )
        """)
        conn.commit()
        conn.close()

    def registrar_pago(self, socio_id, monto, mes_correspondiente, metodo_pago='efectivo', observaciones=''):
        """Registra un nuevo pago."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        fecha_pago = datetime.now().strftime('%Y-%m-%d')
        
        c.execute("""
            INSERT INTO pagos (socio_id, monto, fecha_pago, mes_correspondiente, metodo_pago, observaciones)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (socio_id, monto, fecha_pago, mes_correspondiente, metodo_pago, observaciones))
        
        conn.commit()
        pago_id = c.lastrowid
        conn.close()
        
        return pago_id

    def obtener_pagos(self):
        """Obtiene todos los pagos con información del socio."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                p.id,
                s.nombre || ' ' || s.apellido AS socio,
                p.monto,
                p.fecha_pago,
                p.mes_correspondiente,
                p.metodo_pago,
                p.observaciones,
                s.id as socio_id
            FROM pagos p
            JOIN socios s ON p.socio_id = s.id
            ORDER BY p.fecha_pago DESC
        """)
        
        pagos = c.fetchall()
        conn.close()
        return pagos

    def obtener_pagos_por_socio(self, socio_id):
        """Obtiene el historial de pagos de un socio específico."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                id, monto, fecha_pago, mes_correspondiente, metodo_pago, observaciones
            FROM pagos
            WHERE socio_id = ?
            ORDER BY fecha_pago DESC
        """, (socio_id,))
        
        pagos = c.fetchall()
        conn.close()
        return pagos

    def obtener_pago_por_id(self, pago_id):
        """Obtiene un pago específico por su ID."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                p.id,
                p.socio_id,
                s.nombre || ' ' || s.apellido AS socio,
                p.monto,
                p.fecha_pago,
                p.mes_correspondiente,
                p.metodo_pago,
                p.observaciones
            FROM pagos p
            JOIN socios s ON p.socio_id = s.id
            WHERE p.id = ?
        """, (pago_id,))
        
        pago = c.fetchone()
        conn.close()
        return pago

    def actualizar_pago(self, pago_id, monto, mes_correspondiente, metodo_pago, observaciones):
        """Actualiza un pago existente."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            UPDATE pagos
            SET monto = ?, mes_correspondiente = ?, metodo_pago = ?, observaciones = ?
            WHERE id = ?
        """, (monto, mes_correspondiente, metodo_pago, observaciones, pago_id))
        
        conn.commit()
        conn.close()

    def eliminar_pago(self, pago_id):
        """Elimina un pago."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("DELETE FROM pagos WHERE id = ?", (pago_id,))
        
        conn.commit()
        conn.close()

    def obtener_pagos_filtrados(self, socio_id=None, fecha_desde=None, fecha_hasta=None, mes=None, anio=None):
        """Obtiene pagos con filtros específicos."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = """
            SELECT 
                p.id,
                s.nombre || ' ' || s.apellido AS socio,
                p.monto,
                p.fecha_pago,
                p.mes_correspondiente,
                p.metodo_pago,
                p.observaciones,
                s.id as socio_id
            FROM pagos p
            JOIN socios s ON p.socio_id = s.id
            WHERE 1=1
        """
        
        params = []
        
        if socio_id:
            query += " AND p.socio_id = ?"
            params.append(socio_id)
        
        if fecha_desde:
            query += " AND p.fecha_pago >= ?"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND p.fecha_pago <= ?"
            params.append(fecha_hasta)
        
        if mes:
            query += " AND p.mes_correspondiente LIKE ?"
            params.append(f"%-{mes}-%")
        
        if anio:
            query += " AND p.mes_correspondiente LIKE ?"
            params.append(f"{anio}-%")
        
        query += " ORDER BY p.fecha_pago DESC"
        
        c.execute(query, params)
        pagos = c.fetchall()
        conn.close()
        
        return pagos

    def obtener_ultimo_pago_socio(self, socio_id):
        """Obtiene el último pago de un socio."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT id, monto, fecha_pago, mes_correspondiente
            FROM pagos
            WHERE socio_id = ?
            ORDER BY fecha_pago DESC
            LIMIT 1
        """, (socio_id,))
        
        pago = c.fetchone()
        conn.close()
        return pago

    def obtener_estadisticas_pagos(self, fecha_desde=None, fecha_hasta=None):
        """Obtiene estadísticas de pagos."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = """
            SELECT 
                COUNT(*) as total_pagos,
                SUM(monto) as total_ingresos,
                AVG(monto) as promedio_pago,
                COUNT(DISTINCT socio_id) as socios_pagaron
            FROM pagos
            WHERE 1=1
        """
        
        params = []
        
        if fecha_desde:
            query += " AND fecha_pago >= ?"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND fecha_pago <= ?"
            params.append(fecha_hasta)
        
        c.execute(query, params)
        stats = c.fetchone()
        conn.close()
        
        return {
            'total_pagos': stats[0] or 0,
            'total_ingresos': stats[1] or 0,
            'promedio_pago': stats[2] or 0,
            'socios_pagaron': stats[3] or 0
        }

    def obtener_pagos_por_metodo(self, fecha_desde=None, fecha_hasta=None):
        """Obtiene el total de pagos agrupados por método."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = """
            SELECT metodo_pago, COUNT(*), SUM(monto)
            FROM pagos
            WHERE 1=1
        """
        
        params = []
        
        if fecha_desde:
            query += " AND fecha_pago >= ?"
            params.append(fecha_desde)
        
        if fecha_hasta:
            query += " AND fecha_pago <= ?"
            params.append(fecha_hasta)
        
        query += " GROUP BY metodo_pago"
        
        c.execute(query, params)
        metodos = c.fetchall()
        conn.close()
        
        return metodos

    def verificar_pago_mes(self, socio_id, mes_correspondiente):
        """Verifica si un socio ya pagó un mes específico."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT COUNT(*)
            FROM pagos
            WHERE socio_id = ? AND mes_correspondiente = ?
        """, (socio_id, mes_correspondiente))
        
        count = c.fetchone()[0]
        conn.close()
        
        return count > 0

    def obtener_deudores(self):
        """Obtiene lista de socios con pagos vencidos."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                s.id,
                s.nombre || ' ' || s.apellido AS socio,
                s.telefono,
                MAX(p.fecha_pago) as ultimo_pago,
                COALESCE(pl.duracion_dias, 30) as duracion,
                julianday('now') - julianday(MAX(p.fecha_pago)) as dias_sin_pagar
            FROM socios s
            LEFT JOIN pagos p ON s.id = p.socio_id
            LEFT JOIN planes pl ON s.plan_id = pl.id
            GROUP BY s.id
            HAVING dias_sin_pagar > duracion OR ultimo_pago IS NULL
            ORDER BY dias_sin_pagar DESC
        """)
        
        deudores = c.fetchall()
        conn.close()
        
        return deudores