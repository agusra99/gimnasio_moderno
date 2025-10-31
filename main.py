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

        # Crear controladores individuales
        self.members_controller = MembersController(self.db_connection.db_name)
        self.plans_controller = PlansController(self.db_connection.db_name)

        # Crear controlador de pagos
        self.payments_controller = PaymentsController(self.db_connection.db_name)

        # Gestor de temas
        self.theme_manager = ThemeManager()

        # Inicializar servicio de email
        self.email_service = EmailService()
        self.cargar_config_email()

        # Configuración de ventana
        self.setWindowTitle("Sistema de Gestión de Gimnasio")
        self.setMinimumSize(1000, 700)
        
        # Aplicar tema inicial
        self.setStyleSheet(self.theme_manager.get_theme())

        # Layout principal
        container = QWidget()
        main_layout = QHBoxLayout(container)

        # Panel lateral
        side_panel = QFrame()
        side_layout = QVBoxLayout(side_panel)
        side_layout.setAlignment(Qt.AlignTop)
        side_panel.setFixedWidth(200)
        side_panel.setObjectName("sidePanel")
        
        # Agregar estilo específico al panel lateral
        side_panel.setStyleSheet("""
            #sidePanel {
                background-color: transparent;
                border-radius: 8px;
            }
        """)

        # Logo/Título del sistema
        lbl_sistema = QLabel("🏋️ Gimnasio AR")
        lbl_sistema.setAlignment(Qt.AlignCenter)
        lbl_sistema.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0078d7;
            padding: 20px 10px;
            background-color: transparent;
        """)
        side_layout.addWidget(lbl_sistema)

        # Botones del menú
        self.btnSocios = QPushButton("👥 Socios")
        self.btnPlanes = QPushButton("📅 Planes")
        self.btnPagos = QPushButton("💰 Pagos")
        self.btnNotificaciones = QPushButton("🔔 Notificaciones")
        self.btnReportes = QPushButton("📈 Reportes")
        self.btnEmails = QPushButton("📧 Config. Emails")
        self.btnTema = QPushButton("🌙 Cambiar Tema")
        self.btnSalir = QPushButton("🚪 Salir")

        # Estilo de botones del menú
        menu_button_style = """
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

        for btn in [self.btnSocios, self.btnPlanes, self.btnPagos, 
                    self.btnNotificaciones, self.btnReportes, self.btnEmails, 
                    self.btnTema, self.btnSalir]:
            btn.setStyleSheet(menu_button_style)
            side_layout.addWidget(btn)
            side_layout.addSpacing(5)

        side_layout.addStretch()

        # Contenido principal - Dashboard
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Cargar el dashboard principal
        try:
            from views.dashboard_home import DashboardHome
            from models.notifications_model import NotificationsModel
            
            notifications_model = NotificationsModel(self.db_connection.db_name)
            self.dashboard_widget = DashboardHome(self.db_connection.db_name, notifications_model)
            content_layout.addWidget(self.dashboard_widget)
        except Exception as e:
            # Si hay error, mostrar mensaje simple
            error_label = QLabel(f"Error al cargar dashboard:\n{str(e)}")
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red; padding: 50px;")
            content_layout.addWidget(error_label)

        # Agregar al layout principal
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
        """Conecta los botones del menú con las funciones."""
        self.btnSocios.clicked.connect(self.abrir_socios)
        self.btnPlanes.clicked.connect(self.abrir_planes)
        self.btnPagos.clicked.connect(self.abrir_pagos)
        self.btnNotificaciones.clicked.connect(self.abrir_notificaciones)
        self.btnReportes.clicked.connect(self.abrir_reportes)
        self.btnEmails.clicked.connect(self.abrir_email_settings)
        self.btnTema.clicked.connect(self.cambiar_tema)
        self.btnSalir.clicked.connect(self.confirm_exit)

    def abrir_socios(self):
        """Abre la ventana de gestión de socios."""
        try:
            from views.members import MembersView
            self.members_window = MembersView(self.members_controller)
            self.members_window.setWindowTitle("Gestión de Socios")
            self.members_window.resize(1000, 700)
            
            # Pasar el servicio de email a la vista de miembros
            if hasattr(self, 'email_service'):
                self.members_window.email_service = self.email_service
            
            # Aplicar tema actual
            self.members_window.setStyleSheet(self.theme_manager.get_theme())
            self.members_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de Socios:\n{str(e)}")

    def abrir_planes(self):
        """Abre la ventana de gestión de planes."""
        try:
            from views.plans import PlansView
            self.plans_window = PlansView(self.plans_controller)
            self.plans_window.setWindowTitle("Gestión de Planes")
            self.plans_window.resize(800, 600)
            
            # Aplicar tema actual
            self.plans_window.setStyleSheet(self.theme_manager.get_theme())
            self.plans_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de Planes:\n{str(e)}")

    def abrir_pagos(self):
        """Abre la ventana de gestión de pagos."""
        try:
            from views.payments_complete import PaymentsCompleteView
            self.payments_window = PaymentsCompleteView(self.payments_controller, self.email_service)
            self.payments_window.setWindowTitle("Gestión de Pagos")
            self.payments_window.resize(1400, 900)
            
            # Aplicar tema actual
            self.payments_window.setStyleSheet(self.theme_manager.get_theme())
            self.payments_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de Pagos:\n{str(e)}")

    def abrir_notificaciones(self):
        """Abre la ventana de notificaciones."""
        try:
            from views.notifications import NotificationsView
            from models.notifications_model import NotificationsModel
            
            notifications_model = NotificationsModel(self.db_connection.db_name)
            self.notifications_window = NotificationsView(notifications_model)
            self.notifications_window.setWindowTitle("Centro de Notificaciones")
            self.notifications_window.resize(1000, 700)
            
            # Pasar el servicio de email
            if hasattr(self, 'email_service'):
                self.notifications_window.email_service = self.email_service
            
            # Aplicar tema actual
            self.notifications_window.setStyleSheet(self.theme_manager.get_theme())
            self.notifications_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Notificaciones:\n{str(e)}")

    def abrir_reportes(self):
        """Abre la ventana de reportes y estadísticas."""
        try:
            from views.reports import ReportsView
            self.reports_window = ReportsView(self.db_connection.db_name)
            self.reports_window.setWindowTitle("Reportes y Estadísticas")
            self.reports_window.resize(1200, 800)
            
            # Aplicar tema actual
            self.reports_window.setStyleSheet(self.theme_manager.get_theme())
            self.reports_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Reportes:\n{str(e)}")

    def abrir_email_settings(self):
        """Abre la ventana de configuración de emails."""
        try:
            from email_config import EmailConfigView
            
            self.email_config_window = EmailConfigView(self.email_service)
            self.email_config_window.setWindowTitle("Configuración de Emails")
            self.email_config_window.resize(800, 700)
            
            # Aplicar tema actual
            self.email_config_window.setStyleSheet(self.theme_manager.get_theme())
            self.email_config_window.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo abrir Config. de Emails:\n{str(e)}")

    def cambiar_tema(self):
        """Cambia entre tema claro y oscuro."""
        nuevo_tema = self.theme_manager.toggle_theme()
        self.setStyleSheet(nuevo_tema)
        
        # Actualizar panel lateral
        if self.theme_manager.is_dark():
            self.findChild(QFrame, "sidePanel").setStyleSheet("""
                #sidePanel {
                    background-color: #2d2d2d;
                    border-radius: 8px;
                }
            """)
        else:
            self.findChild(QFrame, "sidePanel").setStyleSheet("""
                #sidePanel {
                    background-color: #e8e8e8;
                    border-radius: 8px;
                }
            """)
        
        # Mostrar mensaje
        tema_nombre = "Oscuro" if self.theme_manager.is_dark() else "Claro"
        QMessageBox.information(
            self,
            "Tema Cambiado",
            f"Se aplicó el tema {tema_nombre}.\nLas ventanas abiertas mantendrán su tema actual."
        )

    def confirm_exit(self):
        """Confirma la salida antes de cerrar."""
        reply = QMessageBox.question(
            self,
            "Salir del sistema",
            "¿Seguro que deseas salir?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.db_connection.close()
            self.close()

    def keyPressEvent(self, event):
        """Permite cerrar con Escape."""
        if event.key() == Qt.Key_Escape:
            self.confirm_exit()

    def closeEvent(self, event):
        """Se ejecuta al cerrar la ventana."""
        self.db_connection.close()
        event.accept()


# IMPORTANTE: Esta función debe estar FUERA de la clase MainWindow
def main():
    """Función principal."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


# Punto de entrada del programa
if __name__ == "__main__":
    main()