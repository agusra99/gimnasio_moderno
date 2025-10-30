"""
controllers/payments_controller.py
Controlador para gestionar todas las operaciones relacionadas con pagos de socios.
"""

import sqlite3
from datetime import datetime
from models.payments_model import PaymentsModel


class PaymentsController:
    def __init__(self, db_path):
        """
        Inicializa el controlador de pagos.
        
        Args:
            db_path (str): Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.payments_model = PaymentsModel(db_path)
        self.conn = None

    def _get_connection(self):
        """Obtiene una conexión a la base de datos."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
        return self.conn

    def registrar_pago(self, socio_id, monto, mes_correspondiente, metodo_pago='efectivo', observaciones=''):
        """
        Registra un nuevo pago en el sistema.
        
        Args:
            socio_id (int): ID del socio que realiza el pago
            monto (float): Monto del pago
            mes_correspondiente (str): Mes al que corresponde el pago (formato: YYYY-MM)
            metodo_pago (str): Método de pago utilizado
            observaciones (str): Notas adicionales sobre el pago
        
        Returns:
            int: ID del pago registrado
        """
        try:
            pago_id = self.payments_model.registrar_pago(
                socio_id, 
                monto, 
                mes_correspondiente, 
                metodo_pago, 
                observaciones
            )
            return pago_id
        except Exception as e:
            print(f"Error al registrar pago: {e}")
            raise

    def obtener_todos_los_pagos(self):
        """
        Obtiene todos los pagos registrados con información del socio.
        
        Returns:
            list: Lista de tuplas con información de pagos
        """
        try:
            return self.payments_model.obtener_pagos()
        except Exception as e:
            print(f"Error al obtener pagos: {e}")
            return []

    def obtener_pagos_socio(self, socio_id):
        """
        Obtiene el historial de pagos de un socio específico.
        
        Args:
            socio_id (int): ID del socio
        
        Returns:
            list: Lista de pagos del socio
        """
        try:
            return self.payments_model.obtener_pagos_por_socio(socio_id)
        except Exception as e:
            print(f"Error al obtener pagos del socio: {e}")
            return []

    def obtener_pago(self, pago_id):
        """
        Obtiene un pago específico por su ID.
        
        Args:
            pago_id (int): ID del pago
        
        Returns:
            tuple: Información del pago
        """
        try:
            return self.payments_model.obtener_pago_por_id(pago_id)
        except Exception as e:
            print(f"Error al obtener pago: {e}")
            return None

    def actualizar_pago(self, pago_id, monto, mes_correspondiente, metodo_pago, observaciones):
        """
        Actualiza la información de un pago existente.
        
        Args:
            pago_id (int): ID del pago a actualizar
            monto (float): Nuevo monto
            mes_correspondiente (str): Nuevo mes correspondiente
            metodo_pago (str): Nuevo método de pago
            observaciones (str): Nuevas observaciones
        """
        try:
            self.payments_model.actualizar_pago(
                pago_id, 
                monto, 
                mes_correspondiente, 
                metodo_pago, 
                observaciones
            )
        except Exception as e:
            print(f"Error al actualizar pago: {e}")
            raise

    def eliminar_pago(self, pago_id):
        """
        Elimina un pago del sistema.
        
        Args:
            pago_id (int): ID del pago a eliminar
        """
        try:
            self.payments_model.eliminar_pago(pago_id)
        except Exception as e:
            print(f"Error al eliminar pago: {e}")
            raise

    def buscar_pagos(self, socio_id=None, fecha_desde=None, fecha_hasta=None, mes=None, anio=None):
        """
        Busca pagos aplicando filtros específicos.
        
        Args:
            socio_id (int, optional): Filtrar por socio
            fecha_desde (str, optional): Fecha de inicio (YYYY-MM-DD)
            fecha_hasta (str, optional): Fecha de fin (YYYY-MM-DD)
            mes (str, optional): Mes a filtrar (MM)
            anio (str, optional): Año a filtrar (YYYY)
        
        Returns:
            list: Lista de pagos que cumplen los filtros
        """
        try:
            return self.payments_model.obtener_pagos_filtrados(
                socio_id, 
                fecha_desde, 
                fecha_hasta, 
                mes, 
                anio
            )
        except Exception as e:
            print(f"Error al buscar pagos: {e}")
            return []

    def obtener_estadisticas(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene estadísticas de pagos para un período específico.
        
        Args:
            fecha_desde (str, optional): Fecha de inicio
            fecha_hasta (str, optional): Fecha de fin
        
        Returns:
            dict: Diccionario con estadísticas (total_pagos, total_ingresos, etc.)
        """
        try:
            return self.payments_model.obtener_estadisticas_pagos(fecha_desde, fecha_hasta)
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {
                'total_pagos': 0,
                'total_ingresos': 0,
                'promedio_pago': 0,
                'socios_pagaron': 0
            }

    def obtener_pagos_por_metodo(self, fecha_desde=None, fecha_hasta=None):
        """
        Obtiene el total de pagos agrupados por método de pago.
        
        Args:
            fecha_desde (str, optional): Fecha de inicio
            fecha_hasta (str, optional): Fecha de fin
        
        Returns:
            list: Lista de tuplas (metodo, cantidad, total)
        """
        try:
            return self.payments_model.obtener_pagos_por_metodo(fecha_desde, fecha_hasta)
        except Exception as e:
            print(f"Error al obtener pagos por método: {e}")
            return []

    def verificar_duplicado(self, socio_id, mes_correspondiente):
        """
        Verifica si ya existe un pago para un socio en un mes específico.
        
        Args:
            socio_id (int): ID del socio
            mes_correspondiente (str): Mes a verificar (YYYY-MM)
        
        Returns:
            bool: True si ya existe un pago, False en caso contrario
        """
        try:
            return self.payments_model.verificar_pago_mes(socio_id, mes_correspondiente)
        except Exception as e:
            print(f"Error al verificar duplicado: {e}")
            return False

    def obtener_deudores(self):
        """
        Obtiene lista de socios con pagos vencidos.
        
        Returns:
            list: Lista de socios deudores con información de último pago
        """
        try:
            return self.payments_model.obtener_deudores()
        except Exception as e:
            print(f"Error al obtener deudores: {e}")
            return []

    def obtener_ultimo_pago_socio(self, socio_id):
        """
        Obtiene el último pago registrado de un socio.
        
        Args:
            socio_id (int): ID del socio
        
        Returns:
            tuple: Información del último pago o None
        """
        try:
            return self.payments_model.obtener_ultimo_pago_socio(socio_id)
        except Exception as e:
            print(f"Error al obtener último pago: {e}")
            return None

    def obtener_socios(self):
        """
        Obtiene la lista de todos los socios activos.
        Esta función consulta directamente la tabla de socios.
        
        Returns:
            list: Lista de tuplas con información de socios (id, nombre, apellido, ...)
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, apellido, telefono, email, fecha_inscripcion, activo
                FROM socios
                WHERE activo = 1
                ORDER BY apellido, nombre
            """)
            
            socios = cursor.fetchall()
            return socios
        except Exception as e:
            print(f"Error al obtener socios: {e}")
            return []

    def obtener_resumen_mensual(self, anio, mes):
        """
        Obtiene un resumen de pagos para un mes específico.
        
        Args:
            anio (int): Año
            mes (int): Mes (1-12)
        
        Returns:
            dict: Resumen con totales y detalles del mes
        """
        try:
            mes_str = f"{anio}-{str(mes).zfill(2)}"
            
            # Obtener pagos del mes
            pagos = self.buscar_pagos(mes=str(mes).zfill(2), anio=str(anio))
            
            # Calcular totales
            total_ingresos = sum(pago[2] for pago in pagos)
            cantidad_pagos = len(pagos)
            socios_pagaron = len(set(pago[7] for pago in pagos))
            
            # Obtener pagos por método
            metodos = {}
            for pago in pagos:
                metodo = pago[5] if pago[5] else 'efectivo'
                if metodo not in metodos:
                    metodos[metodo] = {'cantidad': 0, 'total': 0}
                metodos[metodo]['cantidad'] += 1
                metodos[metodo]['total'] += pago[2]
            
            return {
                'mes': mes_str,
                'total_ingresos': total_ingresos,
                'cantidad_pagos': cantidad_pagos,
                'socios_pagaron': socios_pagaron,
                'metodos': metodos,
                'pagos': pagos
            }
        except Exception as e:
            print(f"Error al obtener resumen mensual: {e}")
            return {
                'mes': f"{anio}-{str(mes).zfill(2)}",
                'total_ingresos': 0,
                'cantidad_pagos': 0,
                'socios_pagaron': 0,
                'metodos': {},
                'pagos': []
            }

    def generar_reporte_anual(self, anio):
        """
        Genera un reporte anual con estadísticas mes a mes.
        
        Args:
            anio (int): Año del reporte
        
        Returns:
            dict: Reporte completo del año
        """
        try:
            reporte = {
                'anio': anio,
                'meses': [],
                'total_anual': 0,
                'promedio_mensual': 0
            }
            
            for mes in range(1, 13):
                resumen = self.obtener_resumen_mensual(anio, mes)
                reporte['meses'].append(resumen)
                reporte['total_anual'] += resumen['total_ingresos']
            
            reporte['promedio_mensual'] = reporte['total_anual'] / 12
            
            return reporte
        except Exception as e:
            print(f"Error al generar reporte anual: {e}")
            return {
                'anio': anio,
                'meses': [],
                'total_anual': 0,
                'promedio_mensual': 0
            }

    def __del__(self):
        """Cierra la conexión al destruir el objeto."""
        if self.conn:
            self.conn.close()