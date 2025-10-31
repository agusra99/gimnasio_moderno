
"""
views/email_config.py
Vista para configurar el envío automático de emails.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QFormLayout, QMessageBox, QHBoxLayout, QTextEdit
)
from PySide6.QtCore import Qt
import json
import os


class EmailConfigView(QWidget):
    def __init__(self, email_service):
        super().__init__()
        self.email_service = email_service
        self.config_file = "email_config.json"
        self.init_ui()
        self.cargar_configuracion()

    def init_ui(self):
        layout = QVBoxLayout()

        # Título
        title = QLabel("📧 Configuración de Emails")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Información
        info_frame = QGroupBox("ℹ️ Información")
        info_layout = QVBoxLayout()
        info_text = QLabel(
            "Para enviar emails automáticos, necesitás configurar una cuenta de email.\n\n"
            "<b>Para Gmail:</b>\n"
            "1. Usá tu cuenta de Gmail\n"
            "2. Habilitá la verificación en dos pasos\n"
            "3. Creá una 'Contraseña de aplicación' en: https://myaccount.google.com/apppasswords\n"
            "4. Usá esa contraseña aquí (no tu contraseña normal)\n\n"
            "<b>Servidor SMTP:</b> smtp.gmail.com\n"
            "<b>Puerto:</b> 587"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 12px; padding: 10px; color: #666;")
        info_layout.addWidget(info_text)
        info_frame.setLayout(info_layout)
        layout.addWidget(info_frame)

        # Formulario de configuración
        config_group = QGroupBox("⚙️ Configuración SMTP")
        config_layout = QFormLayout()

        self.input_smtp_server = QLineEdit()
        self.input_smtp_server.setPlaceholderText("smtp.gmail.com")
        self.input_smtp_server.setText("smtp.gmail.com")

        self.input_smtp_port = QLineEdit()
        self.input_smtp_port.setPlaceholderText("587")
        self.input_smtp_port.setText("587")

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("tugym@gmail.com")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Contraseña de aplicación")
        self.input_password.setEchoMode(QLineEdit.Password)

        config_layout.addRow("Servidor SMTP:", self.input_smtp_server)
        config_layout.addRow("Puerto:", self.input_smtp_port)
        config_layout.addRow("Email:", self.input_email)
        config_layout.addRow("Contraseña:", self.input_password)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

        # Botones de configuración
        btn_layout = QHBoxLayout()

        self.btn_probar = QPushButton("🧪 Probar Conexión")
        self.btn_probar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #2196F3;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #1976D2;
            }
        """)
        self.btn_probar.clicked.connect(self.probar_conexion)

        self.btn_guardar = QPushButton("💾 Guardar Configuración")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #4CAF50;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #388E3C;
            }
        """)
        self.btn_guardar.clicked.connect(self.guardar_configuracion)

        self.btn_enviar_prueba = QPushButton("📧 Enviar Email de Prueba")
        self.btn_enviar_prueba.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #FF9800;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #F57C00;
            }
        """)
        self.btn_enviar_prueba.clicked.connect(self.enviar_prueba)

        btn_layout.addWidget(self.btn_probar)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_enviar_prueba)
        layout.addLayout(btn_layout)

        # Sección para enviar email personalizado
        envio_group = QGroupBox("📤 Enviar Email Personalizado")
        envio_layout = QFormLayout()

        self.input_destinatario = QLineEdit()
        self.input_destinatario.setPlaceholderText("ejemplo@gmail.com")

        self.input_nombre_dest = QLineEdit()
        self.input_nombre_dest.setPlaceholderText("Nombre del destinatario")

        self.btn_enviar_custom = QPushButton("📧 Enviar Email")
        self.btn_enviar_custom.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background: #9C27B0;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7B1FA2;
            }
        """)
        self.btn_enviar_custom.clicked.connect(self.enviar_email_personalizado)

        envio_layout.addRow("Email destinatario:", self.input_destinatario)
        envio_layout.addRow("Nombre:", self.input_nombre_dest)
        envio_layout.addRow("", self.btn_enviar_custom)

        envio_group.setLayout(envio_layout)
        layout.addWidget(envio_group)

        # Área de logs
        logs_group = QGroupBox("📋 Registro de Actividad")
        logs_layout = QVBoxLayout()

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setMaximumHeight(200)
        self.logs_text.setStyleSheet("background-color: transparent; font-family: monospace;")

        logs_layout.addWidget(self.logs_text)
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)

        layout.addStretch()
        self.setLayout(layout)

    def agregar_log(self, mensaje):
        """Agrega un mensaje al log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs_text.append(f"[{timestamp}] {mensaje}")

    def cargar_configuracion(self):
        """Carga la configuración guardada."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                self.input_smtp_server.setText(config.get('smtp_server', 'smtp.gmail.com'))
                self.input_smtp_port.setText(config.get('smtp_port', '587'))
                self.input_email.setText(config.get('email', ''))
                self.input_password.setText(config.get('password', ''))
                
                # Configurar el servicio
                if config.get('email') and config.get('password'):
                    self.email_service.smtp_server = config.get('smtp_server', 'smtp.gmail.com')
                    self.email_service.smtp_port = int(config.get('smtp_port', 587))
                    self.email_service.configurar(config.get('email'), config.get('password'))
                    self.agregar_log("✓ Configuración cargada desde archivo")
        except Exception as e:
            self.agregar_log(f"⚠️ Error al cargar configuración: {e}")

    def guardar_configuracion(self):
        """Guarda la configuración en un archivo."""
        try:
            config = {
                'smtp_server': self.input_smtp_server.text().strip(),
                'smtp_port': self.input_smtp_port.text().strip(),
                'email': self.input_email.text().strip(),
                'password': self.input_password.text().strip()
            }
            
            if not config['email'] or not config['password']:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Debés completar el email y la contraseña."
                )
                return
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            
            # Configurar el servicio
            self.email_service.smtp_server = config['smtp_server']
            self.email_service.smtp_port = int(config['smtp_port'])
            self.email_service.configurar(config['email'], config['password'])
            
            self.agregar_log("✓ Configuración guardada exitosamente")
            QMessageBox.information(
                self,
                "Éxito",
                "Configuración guardada correctamente."
            )
        except Exception as e:
            self.agregar_log(f"✗ Error al guardar: {e}")
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")

    def probar_conexion(self):
        """Prueba la conexión con el servidor SMTP."""
        smtp_server = self.input_smtp_server.text().strip()
        smtp_port = self.input_smtp_port.text().strip()
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()
        
        if not email or not password:
            QMessageBox.warning(
                self,
                "Error",
                "Debés completar el email y la contraseña."
            )
            return
        
        self.agregar_log("🔄 Probando conexión...")
        
        try:
            self.email_service.smtp_server = smtp_server
            self.email_service.smtp_port = int(smtp_port)
            self.email_service.configurar(email, password)
            
            exito, mensaje = self.email_service.probar_conexion()
            
            if exito:
                self.agregar_log("✓ Conexión exitosa!")
                QMessageBox.information(
                    self,
                    "Éxito",
                    "¡Conexión exitosa! La configuración es correcta."
                )
            else:
                self.agregar_log(f"✗ Error: {mensaje}")
                QMessageBox.warning(self, "Error", mensaje)
                
        except Exception as e:
            self.agregar_log(f"✗ Error inesperado: {e}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def enviar_prueba(self):
        """Envía un email de prueba."""
        email = self.input_email.text().strip()
        
        if not self.email_service.configurado:
            QMessageBox.warning(
                self,
                "Error",
                "Primero debés guardar la configuración."
            )
            return
        
        self.agregar_log("📧 Enviando email de prueba...")
        
        try:
            exito, mensaje = self.email_service.enviar_recordatorio_pago(
                email,
                "Usuario de Prueba",
                dias_vencido=0,
                ultimo_pago="01/01/2024"
            )
            
            if exito:
                self.agregar_log("✓ Email de prueba enviado!")
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Email de prueba enviado a {email}.\nRevisá tu bandeja de entrada."
                )
            else:
                self.agregar_log(f"✗ Error: {mensaje}")
                QMessageBox.warning(self, "Error", mensaje)
                
        except Exception as e:
            self.agregar_log(f"✗ Error: {e}")
            QMessageBox.critical(self, "Error", f"Error al enviar: {str(e)}")

    def enviar_email_personalizado(self):
        """Envía un email a un destinatario específico."""
        if not self.email_service.configurado:
            QMessageBox.warning(
                self,
                "Error",
                "Primero debés guardar la configuración."
            )
            return
        
        email_dest = self.input_destinatario.text().strip()
        nombre_dest = self.input_nombre_dest.text().strip()
        
        if not email_dest:
            QMessageBox.warning(
                self,
                "Error",
                "Debés ingresar un email de destinatario."
            )
            return
        
        if not nombre_dest:
            nombre_dest = "Usuario"
        
        self.agregar_log(f"📧 Enviando email a {email_dest}...")
        
        try:
            exito, mensaje = self.email_service.enviar_recordatorio_pago(
                email_dest,
                nombre_dest,
                dias_vencido=0,
                ultimo_pago=None
            )
            
            if exito:
                self.agregar_log(f"✓ Email enviado a {email_dest}!")
                QMessageBox.information(
                    self,
                    "Éxito",
                    f"Email enviado exitosamente a:\n{email_dest}"
                )
                # Limpiar campos
                self.input_destinatario.clear()
                self.input_nombre_dest.clear()
            else:
                self.agregar_log(f"✗ Error: {mensaje}")
                QMessageBox.warning(self, "Error", mensaje)
                
        except Exception as e:
            self.agregar_log(f"✗ Error: {e}")
            QMessageBox.critical(self, "Error", f"Error al enviar: {str(e)}")