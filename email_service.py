"""
email_service.py
Servicio para envío de emails automáticos de notificaciones.
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime


class EmailService:
    """Servicio para enviar emails de notificaciones."""
    
    def __init__(self, smtp_server="smtp.gmail.com", smtp_port=587):
        """
        Inicializa el servicio de email.
        
        Para Gmail:
        - smtp_server: "smtp.gmail.com"
        - smtp_port: 587
        - Necesitás habilitar "Acceso de aplicaciones menos seguras" o usar App Password
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_from = None
        self.password = None
        self.configurado = False

    def configurar(self, email_from, password):
        """Configura las credenciales del email."""
        self.email_from = email_from
        self.password = password
        self.configurado = True

    def enviar_recordatorio_pago(self, email_to, nombre_socio, dias_vencido=None, ultimo_pago=None):
        """Envía un recordatorio de pago vencido."""
        if not self.configurado:
            return False, "Servicio de email no configurado"
        
        try:
            # Crear mensaje
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = email_to
            
            if dias_vencido and dias_vencido > 0:
                msg['Subject'] = f"⚠️ Recordatorio: Pago Vencido - {nombre_socio}"
                
                texto = f"""
                Hola {nombre_socio},
                
                Te recordamos que tu pago está vencido desde hace {dias_vencido} días.
                Último pago registrado: {ultimo_pago}
                
                Te pedimos que te acerques al gimnasio para regularizar tu situación.
                
                Gracias por tu comprensión.
                
                Gimnasio - Sistema de Gestión
                """
                
                html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                      <div style="background-color: #F44336; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h1>⚠️ Recordatorio de Pago</h1>
                      </div>
                      <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px;">
                        <p style="font-size: 16px;">Hola <strong>{nombre_socio}</strong>,</p>
                        <p style="font-size: 14px; color: #666;">
                          Te recordamos que tu pago está <strong style="color: #F44336;">vencido desde hace {dias_vencido} días</strong>.
                        </p>
                        <div style="background-color: #fff3f3; padding: 15px; border-left: 4px solid #F44336; margin: 20px 0;">
                          <p style="margin: 0;"><strong>Último pago registrado:</strong> {ultimo_pago}</p>
                        </div>
                        <p style="font-size: 14px; color: #666;">
                          Te pedimos que te acerques al gimnasio para regularizar tu situación.
                        </p>
                        <p style="font-size: 14px; color: #666; margin-top: 30px;">
                          Gracias por tu comprensión.
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #999; text-align: center;">
                          Sistema de Gestión de Gimnasio<br>
                          Este es un mensaje automático, por favor no responder.
                        </p>
                      </div>
                    </div>
                  </body>
                </html>
                """
            else:
                msg['Subject'] = f"🔔 Recordatorio: Próximo Vencimiento - {nombre_socio}"
                
                texto = f"""
                Hola {nombre_socio},
                
                Te recordamos que tu pago está próximo a vencer.
                
                Te esperamos en el gimnasio para renovar tu membresía.
                
                ¡Gracias!
                
                Gimnasio - Sistema de Gestión
                """
                
                html = f"""
                <html>
                  <body style="font-family: Arial, sans-serif;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                      <div style="background-color: #FF9800; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                        <h1>🔔 Recordatorio de Vencimiento</h1>
                      </div>
                      <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px;">
                        <p style="font-size: 16px;">Hola <strong>{nombre_socio}</strong>,</p>
                        <p style="font-size: 14px; color: #666;">
                          Te recordamos que tu pago está <strong style="color: #FF9800;">próximo a vencer</strong>.
                        </p>
                        <p style="font-size: 14px; color: #666;">
                          Te esperamos en el gimnasio para renovar tu membresía.
                        </p>
                        <p style="font-size: 14px; color: #666; margin-top: 30px;">
                          ¡Gracias!
                        </p>
                        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                        <p style="font-size: 12px; color: #999; text-align: center;">
                          Sistema de Gestión de Gimnasio<br>
                          Este es un mensaje automático, por favor no responder.
                        </p>
                      </div>
                    </div>
                  </body>
                </html>
                """
            
            # Adjuntar partes
            part1 = MIMEText(texto, 'plain')
            part2 = MIMEText(html, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.password)
                server.send_message(msg)
            
            return True, "Email enviado exitosamente"
            
        except Exception as e:
            return False, f"Error al enviar email: {str(e)}"

    def enviar_bienvenida(self, email_to, nombre_socio, plan_nombre):
        """Envía un email de bienvenida a nuevos socios."""
        if not self.configurado:
            return False, "Servicio de email no configurado"
        
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_from
            msg['To'] = email_to
            msg['Subject'] = f"🎉 ¡Bienvenido al Gimnasio, {nombre_socio}!"
            
            html = f"""
            <html>
              <body style="font-family: Arial, sans-serif;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9;">
                  <div style="background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
                    <h1>🎉 ¡Bienvenido!</h1>
                  </div>
                  <div style="background-color: white; padding: 30px; border-radius: 0 0 8px 8px;">
                    <p style="font-size: 18px;">Hola <strong>{nombre_socio}</strong>,</p>
                    <p style="font-size: 14px; color: #666;">
                      ¡Bienvenido a nuestro gimnasio! Estamos muy contentos de tenerte con nosotros.
                    </p>
                    <div style="background-color: #f0f9f0; padding: 15px; border-left: 4px solid #4CAF50; margin: 20px 0;">
                      <p style="margin: 0;"><strong>Tu plan:</strong> {plan_nombre}</p>
                      <p style="margin: 10px 0 0 0;"><strong>Fecha de inscripción:</strong> {datetime.now().strftime('%d/%m/%Y')}</p>
                    </div>
                    <p style="font-size: 14px; color: #666;">
                      Recordá que podés consultar tu estado de pagos y renovaciones en cualquier momento.
                    </p>
                    <p style="font-size: 14px; color: #666; margin-top: 30px;">
                      ¡Nos vemos en el gimnasio!
                    </p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999; text-align: center;">
                      Sistema de Gestión de Gimnasio
                    </p>
                  </div>
                </div>
              </body>
            </html>
            """
            
            part = MIMEText(html, 'html')
            msg.attach(part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.password)
                server.send_message(msg)
            
            return True, "Email de bienvenida enviado"
            
        except Exception as e:
            return False, f"Error al enviar email: {str(e)}"

    def probar_conexion(self):
        """Prueba la conexión con el servidor SMTP."""
        if not self.configurado:
            return False, "Servicio no configurado"
        
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_from, self.password)
            return True, "Conexión exitosa"
        except Exception as e:
            return False, f"Error de conexión: {str(e)}"


# Ejemplo de uso:
"""
# Configurar servicio
email_service = EmailService()
email_service.configurar("tugym@gmail.com", "tu_password_de_app")

# Enviar recordatorio
email_service.enviar_recordatorio_pago(
    "socio@email.com", 
    "Juan Pérez", 
    dias_vencido=15, 
    ultimo_pago="2024-01-15"
)

# Enviar bienvenida
email_service.enviar_bienvenida(
    "nuevosocio@email.com",
    "Ana García",
    "Plan Mensual"
)
"""