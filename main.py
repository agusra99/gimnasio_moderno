import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QMessageBox, QLabel, QFrame, QHBoxLayout
)
from PySide6.QtCore import Qt
from connection import DatabaseConnection
from theme_manager import ThemeManager
import json
import os

# Importación directa sin carpetas - todos los archivos en el mismo directorio
from controllers.members_controller import MembersController
from controllers.plans_controller import PlansController
from controllers.payments_controller import PaymentsController
from email_service import EmailService


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Crear conexión a la base de datos
        self.db_connection = DatabaseConnection("gimnasio.db")

        # Crear controladores
        self.members_controller = MembersController(self.db_connection.db_name)
        self.plans_controller = PlansController(self.db_connection.db_name)
        self.payments_controller = PaymentsController(self.db_connection.db_name)

        # Gestor de temas
        self.theme_manager = ThemeManager()

        # Servicio de email
        self.email_service = EmailService()
        self.cargar_config_email()

        # Configuración ventana principal
        self.setWindowTitle("Sistema de Gestión de Gimnasio")
        self.setMinimumSize(1000, 700)
        self.setStyleSheet(self.theme_manager.get_theme())

        # Layout principal
        container = QWidget()
        main_layout = QHBoxLayout(container)

        # --- Panel lateral ---
        side_panel = QFrame()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setAlignment(Qt.AlignTop)
        side_panel.setFixedWidth(200)
        side_panel.setObjectName("sidePanel")
        side_panel.setStyleSheet("""
            #sidePanel {
                background-color: transparent;
                border-radius: 8px;
            }
        """)

        # Logo/Título
        lbl_sistema = QLabel("🏋️ Gimnasio AR")
        lbl_sistema.setAlignment(Qt.AlignCenter)
        lbl_sistema.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0078d7;
            padding: 20px 10px;
        """)
        side_layout.addWidget(lbl_sistema)

        # Botones del menú
        self.btnSocios = QPushButton("👥 Socios")
        self.btnPlanes = QPushButton("📅 Planes")
        self.btnPagos = QPushButton("💰 Pagos")
        self.btnNotificaciones = QPushButton("🔔 Notificaciones")
        self.btnReportes = QPushButton("📈 Reportes")
        self.btnWhatsapp = QPushButton("💬 WhatsApp")  # ✅ Nuevo botón
        self.btnEmails = QPushButton("📧 Config. Emails")
        self.btnTema = QPushButton("🌙 Cambiar Tema")
        self.btnSalir = QPushButton("🚪 Salir")

        # Estilo botones
        menu_style = """
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 500;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: transparent;
            }
            QPushButton:pressed {
                background-color: transparent;
            }
        """

        for btn in [
            self.btnSocios, self.btnPlanes, self.btnPagos, self.btnNotificaciones,
            self.btnReportes, self.btnWhatsapp, self.btnEmails, self.btnTema, self.btnSalir
        ]:
            btn.setStyleSheet(menu_style)
            side_layout.addWidget(btn)
            side_layout.addSpacing(5)

        side_layout.addStretch()

        # --- Contenido principal (Dashboard) ---
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        try:
            from views.dashboard_home import DashboardHome
            from models.notifications_model import NotificationsModel

            notifications_model = NotificationsModel(self.db_connection.db_name)
            self.dashboard_widget = DashboardHome(self.db_connection.db_name, notifications_model)
            content_layout.addWidget(self.dashboard_widget)
        except Exception as e:
            error_label = QLabel(f"Error al cargar dashboard:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; padding: 50px;")
            content_layout.addWidget(error_label)

        # Añadir panel y contenido al layout principal
        main_layout.addWidget(side_panel)
        main_layout.addWidget(content)
        self.setCentralWidget(container)

        # Conectar botones
        self.setup_connections()

    def cargar_config_email(self):
        """Carga la configuración de email desde el archivo JSON."""
        config_file = "email_config.json"
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                if config.get('email') and config.get('password'):
                    self.email_service.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
                    self.email_service.smtp_port = int(config.get('smtp_port', 587))
                    self.email_service.configurar(config.get('email'), config.get('password'))
                    print("✓ Configuración de email cargada")
        except Exception as e:
            print(f"No se pudo cargar config de email: {e}")

    def setup_connections(self):
        """Conecta los botones del menú con sus acciones."""
        self.btnSocios.clicked.connect(self.abrir_socios)
        self.btnPlanes.clicked.connect(self.abrir_planes)
        self.btnPagos.clicked.connect(self.abrir_pagos)
        self.btnNotificaciones.clicked.connect(self.abrir_notificaciones)
        self.btnReportes.clicked.connect(self.abrir_reportes)
        self.btnWhatsapp.clicked.connect(self.abrir_whatsapp)  # ✅ Nuevo
        self.btnEmails.clicked.connect(self.abrir_email_settings)
        self.btnTema.clicked.connect(self.cambiar_tema)
        self.btnSalir.clicked.connect(self.confirm_exit)

    # === FUNCIONES DE VENTANAS ===

    def abrir_socios(self):
        try:
            from views.members import MembersView
            self.members_window = MembersView(self.members_controller)
            self.members_window.setWindowTitle("Gestión de Socios")
            self.members_window.resize(1000, 700)
            if hasattr(self, 'email_service'):
                self.members_window.email_service = self.email_service
            self.members_window.setStyleSheet(self.theme_manager.get_theme())
            self.members_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Socios:\n{e}")

    def abrir_planes(self):
        try:
            from views.plans import PlansView
            self.plans_window = PlansView(self.plans_controller)
            self.plans_window.setWindowTitle("Gestión de Planes")
            self.plans_window.resize(800, 600)
            self.plans_window.setStyleSheet(self.theme_manager.get_theme())
            self.plans_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Planes:\n{e}")

    def abrir_pagos(self):
        try:
            from views.payments_complete_view import PaymentsCompleteView
            self.payments_window = PaymentsCompleteView(self.payments_controller, self.email_service)
            self.payments_window.setWindowTitle("Gestión de Pagos")
            self.payments_window.resize(1400, 900)
            self.payments_window.setStyleSheet(self.theme_manager.get_theme())
            self.payments_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Pagos:\n{e}")

    def abrir_notificaciones(self):
        try:
            from views.notifications import NotificationsView
            from models.notifications_model import NotificationsModel

            notifications_model = NotificationsModel(self.db_connection.db_name)
            self.notifications_window = NotificationsView(notifications_model)
            self.notifications_window.setWindowTitle("Centro de Notificaciones")
            self.notifications_window.resize(1000, 700)
            if hasattr(self, 'email_service'):
                self.notifications_window.email_service = self.email_service
            self.notifications_window.setStyleSheet(self.theme_manager.get_theme())
            self.notifications_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Notificaciones:\n{e}")

    def abrir_reportes(self):
        try:
            from views.reports import ReportsView
            self.reports_window = ReportsView(self.db_connection.db_name)
            self.reports_window.setWindowTitle("Reportes y Estadísticas")
            self.reports_window.resize(1200, 800)
            self.reports_window.setStyleSheet(self.theme_manager.get_theme())
            self.reports_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Reportes:\n{e}")

    def abrir_whatsapp(self):
        """Abre la ventana de envío de mensajes por WhatsApp."""
        try:
            from views.whatsapp_reminder import WhatsappReminderView
            self.whatsapp_window = WhatsappReminderView(self.db_connection.db_name)
            self.whatsapp_window.setWindowTitle("Enviar mensajes por WhatsApp")
            self.whatsapp_window.resize(900, 600)
            self.whatsapp_window.setStyleSheet(self.theme_manager.get_theme())
            self.whatsapp_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir WhatsApp:\n{e}")

    def abrir_email_settings(self):
        try:
            from email_config import EmailConfigView
            self.email_config_window = EmailConfigView(self.email_service)
            self.email_config_window.setWindowTitle("Configuración de Emails")
            self.email_config_window.resize(800, 700)
            self.email_config_window.setStyleSheet(self.theme_manager.get_theme())
            self.email_config_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Config. Emails:\n{e}")

    # === OTRAS FUNCIONES ===

    def cambiar_tema(self):
        nuevo_tema = self.theme_manager.toggle_theme()
        self.setStyleSheet(nuevo_tema)
        if self.theme_manager.is_dark():
            self.findChild(QFrame, "sidePanel").setStyleSheet("#sidePanel { background-color: #2d2d2d; }")
        else:
            self.findChild(QFrame, "sidePanel").setStyleSheet("#sidePanel { background-color: #e8e8e8; }")
        QMessageBox.information(self, "Tema Cambiado",
                                f"Tema {'Oscuro' if self.theme_manager.is_dark() else 'Claro'} aplicado correctamente.")

    def confirm_exit(self):
        reply = QMessageBox.question(
            self, "Salir del sistema", "¿Seguro que deseas salir?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.db_connection.close()
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.confirm_exit()

    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()


# === FUNCIÓN PRINCIPAL ===
def main():
    from license_controller import LicenseController

    app = QApplication(sys.argv)

    # 🔐 Validar licencia antes de abrir el sistema
    if not LicenseController.validate_license():
        return  # Si la licencia no es válida, no abre el programa

    window = MainWindow()
    window.showMaximized()  # Abre maximizado, no pantalla completa
    sys.exit(app.exec())


if __name__ == "__main__":
    main()