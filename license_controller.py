# license_controller.py
import uuid
import hashlib
import os
from PySide6.QtWidgets import QMessageBox

class LicenseController:
    """Controlador de licencia: valida el uso del sistema en un solo equipo."""

    LICENSE_FILE = "license.key"

    @staticmethod
    def get_machine_id():
        """Obtiene un ID único de la máquina basado en el hardware."""
        try:
            # Obtiene el UUID del sistema (funciona en Windows/Linux)
            unique_id = str(uuid.getnode())
            return hashlib.sha256(unique_id.encode()).hexdigest()
        except Exception as e:
            print(f"Error al obtener ID de hardware: {e}")
            return None

    @staticmethod
    def create_license():
        """Crea una licencia nueva basada en esta PC (solo para desarrollador)."""
        machine_id = LicenseController.get_machine_id()
        license_code = hashlib.sha256((machine_id + "AR-SOFTWARE2024").encode()).hexdigest()
        with open(LicenseController.LICENSE_FILE, "w") as f:
            f.write(license_code)
        print("Licencia generada correctamente para este equipo ✅")

    @staticmethod
    def validate_license():
        """Valida que la licencia instalada coincida con la del equipo."""
        machine_id = LicenseController.get_machine_id()
        if not machine_id:
            return False

        valid_code = hashlib.sha256((machine_id + "AR-SOFTWARE2024").encode()).hexdigest()

        if not os.path.exists(LicenseController.LICENSE_FILE):
            QMessageBox.critical(None, "Licencia no encontrada",
                                 "⚠️ No se encontró un archivo de licencia válido.\n"
                                 "Contactá a AR Servicios de Programación para activarlo.")
            return False

        with open(LicenseController.LICENSE_FILE, "r") as f:
            saved_code = f.read().strip()

        if saved_code != valid_code:
            QMessageBox.critical(None, "Licencia inválida",
                                 "🚫 Esta copia del software no está autorizada para este equipo.\n"
                                 "Comunicate con soporte para registrar tu licencia.")
            return False

        return True
