"""
controllers.py
Controladores que gestionan la lógica entre las vistas y los modelos.
Maneja la carga inicial, pagos atrasados y creación automática de alertas.
"""
from datetime import datetime, timedelta
from models import Socio, Pago, Alerta


class AppController:
    def __init__(self, db_connection):
        self.db = db_connection
        self.socios = Socio(self.db)
        self.pagos = Pago(self.db)
        self.alertas = Alerta(self.db)

    def cargar_datos_iniciales(self):
        # Puede usarse al inicio del programa si se desea poblar datos de prueba
        if not self.socios.obtener_todos():
            self.socios.agregar("Juan", "Pérez", "123456789", "juan@example.com", "Mensual")
            self.socios.agregar("Ana", "Gómez", "987654321", "ana@example.com", "Mensual")

    def generar_alertas_atrasados(self):
        socios = self.socios.obtener_todos()
        hoy = datetime.now()
        limite = hoy - timedelta(days=10)  # Más de 10 días sin pagar

        for socio in socios:
            socio_id = socio[0]
            ultimo_pago = self.pagos.obtener_pagos_por_socio(socio_id)

            if ultimo_pago:
                fecha_ultimo = datetime.strptime(ultimo_pago[0][3], '%Y-%m-%d')
                if fecha_ultimo < limite:
                    mensaje = f"El socio {socio[1]} {socio[2]} tiene pagos atrasados."
                    self.alertas.crear_alerta(socio_id, mensaje)
            else:
                # Socio sin pagos registrados
                mensaje = f"El socio {socio[1]} {socio[2]} no tiene pagos registrados."
                self.alertas.crear_alerta(socio_id, mensaje)

    def obtener_socios(self):
        return self.socios.obtener_todos()

    def registrar_pago(self, socio_id, monto, mes_correspondiente):
        self.pagos.registrar_pago(socio_id, monto, mes_correspondiente)

    def obtener_alertas_no_leidas(self):
        return self.alertas.obtener_no_leidas()

    def marcar_alerta_leida(self, alerta_id):
        self.alertas.marcar_como_leida(alerta_id)
