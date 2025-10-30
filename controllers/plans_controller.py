"""
controllers/plans_controller.py
Controlador para gestionar los planes del gimnasio.
"""

from models.plans_model import *


class PlansController:
    def __init__(self, db_path):
        self.model = PlansModel(db_path)

    def obtener_planes(self):
        """Devuelve todos los planes disponibles."""
        return self.model.obtener_planes()

    def agregar_plan(self, nombre, precio, duracion):
        """Agrega un nuevo plan si los datos son válidos."""
        if not nombre or precio <= 0 or duracion <= 0:
            raise ValueError("Los campos no pueden estar vacíos ni tener valores negativos.")
        self.model.agregar_plan(nombre, precio, duracion)

    def eliminar_plan(self, plan_id):
        """Elimina un plan por ID."""
        self.model.eliminar_plan(plan_id)

    def actualizar_plan(self, plan_id, nombre, precio, duracion):
        """Actualiza los datos de un plan existente."""
        if not nombre or precio <= 0 or duracion <= 0:
            raise ValueError("Los campos no pueden estar vacíos ni tener valores negativos.")
        self.model.actualizar_plan(plan_id, nombre, precio, duracion)
