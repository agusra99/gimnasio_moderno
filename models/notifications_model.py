"""
models/notifications_model.py
Modelo para gestionar notificaciones automáticas del sistema.
"""

import sqlite3
from datetime import datetime, timedelta


class NotificationsModel:
    def __init__(self, db_path):
        self.db_path = db_path
        self.crear_tabla()

    def conectar(self):
        return sqlite3.connect(self.db_path)

    def crear_tabla(self):
        """Crea la tabla de notificaciones si no existe."""
        conn = self.conectar()
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS notificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                socio_id INTEGER NOT NULL,
                tipo TEXT NOT NULL,
                mensaje TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                leida INTEGER DEFAULT 0,
                prioridad TEXT DEFAULT 'normal',
                fecha_vencimiento TEXT,
                FOREIGN KEY(socio_id) REFERENCES socios(id)
            )
        """)
        conn.commit()
        conn.close()

    def crear_notificacion(self, socio_id, tipo, mensaje, prioridad='normal', fecha_vencimiento=None):
        """Crea una nueva notificación."""
        conn = self.conectar()
        c = conn.cursor()
        fecha_creacion = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        c.execute("""
            INSERT INTO notificaciones 
            (socio_id, tipo, mensaje, fecha_creacion, prioridad, fecha_vencimiento)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (socio_id, tipo, mensaje, fecha_creacion, prioridad, fecha_vencimiento))
        
        conn.commit()
        conn.close()

    def obtener_notificaciones_pendientes(self):
        """Obtiene todas las notificaciones no leídas."""
        conn = self.conectar()
        c = conn.cursor()
        c.execute("""
            SELECT n.id, n.socio_id, s.nombre || ' ' || s.apellido AS socio,
                   n.tipo, n.mensaje, n.fecha_creacion, n.prioridad, n.fecha_vencimiento
            FROM notificaciones n
            JOIN socios s ON n.socio_id = s.id
            WHERE n.leida = 0
            ORDER BY 
                CASE n.prioridad
                    WHEN 'alta' THEN 1
                    WHEN 'media' THEN 2
                    ELSE 3
                END,
                n.fecha_creacion DESC
        """)
        notificaciones = c.fetchall()
        conn.close()
        return notificaciones

    def marcar_como_leida(self, notificacion_id):
        """Marca una notificación como leída."""
        conn = self.conectar()
        c = conn.cursor()
        c.execute("UPDATE notificaciones SET leida = 1 WHERE id = ?", (notificacion_id,))
        conn.commit()
        conn.close()

    def verificar_pagos_vencidos(self):
        """Verifica pagos vencidos y crea notificaciones automáticas."""
        conn = self.conectar()
        c = conn.cursor()
        
        # Obtener último pago de cada socio
        c.execute("""
            SELECT s.id, s.nombre, s.apellido, s.telefono,
                   MAX(p.fecha_pago) as ultimo_pago,
                   pl.duracion_dias
            FROM socios s
            LEFT JOIN pagos p ON s.id = p.socio_id
            LEFT JOIN planes pl ON s.plan_id = pl.id
            WHERE s.id NOT IN (
                SELECT socio_id FROM notificaciones 
                WHERE tipo = 'pago_vencido' 
                AND leida = 0
                AND DATE(fecha_creacion) = DATE('now')
            )
            GROUP BY s.id
        """)
        
        socios = c.fetchall()
        notificaciones_creadas = 0
        
        for socio in socios:
            socio_id, nombre, apellido, telefono, ultimo_pago, duracion_dias = socio
            
            if not duracion_dias:
                duracion_dias = 30  # Por defecto 30 días
            
            if ultimo_pago:
                fecha_ultimo = datetime.strptime(ultimo_pago, '%Y-%m-%d')
                dias_transcurridos = (datetime.now() - fecha_ultimo).days
                
                # Pago vencido (más de la duración del plan)
                if dias_transcurridos > duracion_dias:
                    dias_vencidos = dias_transcurridos - duracion_dias
                    mensaje = f"Pago vencido hace {dias_vencidos} días. Último pago: {ultimo_pago}"
                    self.crear_notificacion(socio_id, 'pago_vencido', mensaje, 'alta')
                    notificaciones_creadas += 1
                
                # Próximo a vencer (5 días antes)
                elif dias_transcurridos >= duracion_dias - 5:
                    dias_restantes = duracion_dias - dias_transcurridos
                    mensaje = f"El pago vence en {dias_restantes} días"
                    self.crear_notificacion(socio_id, 'proximo_vencimiento', mensaje, 'media')
                    notificaciones_creadas += 1
            else:
                # Socio sin pagos registrados
                mensaje = "No tiene pagos registrados"
                self.crear_notificacion(socio_id, 'sin_pagos', mensaje, 'alta')
                notificaciones_creadas += 1
        
        conn.close()
        return notificaciones_creadas

    def limpiar_notificaciones_antiguas(self, dias=30):
        """Elimina notificaciones leídas con más de X días."""
        conn = self.conectar()
        c = conn.cursor()
        fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
        
        c.execute("""
            DELETE FROM notificaciones 
            WHERE leida = 1 
            AND DATE(fecha_creacion) < ?
        """, (fecha_limite,))
        
        eliminadas = c.rowcount
        conn.commit()
        conn.close()
        return eliminadas

    def obtener_estadisticas(self):
        """Obtiene estadísticas de notificaciones."""
        conn = self.conectar()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN leida = 0 THEN 1 ELSE 0 END) as pendientes,
                SUM(CASE WHEN prioridad = 'alta' AND leida = 0 THEN 1 ELSE 0 END) as urgentes
            FROM notificaciones
        """)
        
        stats = c.fetchone()
        conn.close()
        return {
            'total': stats[0],
            'pendientes': stats[1],
            'urgentes': stats[2]
        }