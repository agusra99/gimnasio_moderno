"""
auto_integrate_payments.py
Script para integrar automáticamente el módulo de pagos en main.py

Uso: python auto_integrate_payments.py
"""

import os
import shutil
from datetime import datetime


def hacer_backup(archivo):
    """Crea un backup del archivo antes de modificarlo."""
    if os.path.exists(archivo):
        backup = f"{archivo}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(archivo, backup)
        print(f"✅ Backup creado: {backup}")
        return True
    return False


def verificar_archivos():
    """Verifica que existan los archivos necesarios."""
    archivos_necesarios = [
        'models/payments_model.py',
        'controllers/payments_controller.py',
        'views/payments_complete.py'
    ]
    
    faltantes = []
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            faltantes.append(archivo)
    
    if faltantes:
        print("❌ Faltan los siguientes archivos:")
        for archivo in faltantes:
            print(f"   - {archivo}")
        return False
    
    print("✅ Todos los archivos necesarios están presentes")
    return True


def integrar_en_main():
    """Integra el módulo de pagos en main.py"""
    
    if not os.path.exists('main.py'):
        print("❌ No se encontró el archivo main.py")
        return False
    
    # Hacer backup
    if not hacer_backup('main.py'):
        print("❌ No se pudo crear el backup")
        return False
    
    # Leer main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    modificado = False
    
    # 1. Agregar importación
    if 'from controllers.payments_controller import PaymentsController' not in contenido:
        # Buscar donde agregar la importación
        if 'from controllers.plans_controller import PlansController' in contenido:
            contenido = contenido.replace(
                'from controllers.plans_controller import PlansController',
                'from controllers.plans_controller import PlansController\n'
                'from controllers.payments_controller import PaymentsController'
            )
            print("✅ Importación agregada")
            modificado = True
    else:
        print("ℹ️  Importación ya existe")
    
    # 2. Agregar controlador en __init__
    if 'self.payments_controller = PaymentsController' not in contenido:
        # Buscar después de plans_controller
        if 'self.plans_controller = PlansController' in contenido:
            contenido = contenido.replace(
                'self.plans_controller = PlansController(self.db_connection.db_name)',
                'self.plans_controller = PlansController(self.db_connection.db_name)\n\n'
                '        # Crear controlador de pagos\n'
                '        self.payments_controller = PaymentsController(self.db_connection.db_name)'
            )
            print("✅ Controlador agregado")
            modificado = True
    else:
        print("ℹ️  Controlador ya existe")
    
    # 3. Agregar botón
    if 'self.btnPagos = QPushButton' not in contenido:
        if 'self.btnPlanes = QPushButton' in contenido:
            contenido = contenido.replace(
                'self.btnPlanes = QPushButton("📅 Planes")',
                'self.btnPlanes = QPushButton("📅 Planes")\n'
                '        self.btnPagos = QPushButton("💰 Pagos")'
            )
            print("✅ Botón agregado")
            modificado = True
    else:
        print("ℹ️  Botón ya existe")
    
    # 4. Agregar botón al bucle de estilos
    if 'self.btnPagos' not in contenido.split('for btn in')[1].split(']:')[0]:
        contenido = contenido.replace(
            'for btn in [self.btnSocios, self.btnPlanes,',
            'for btn in [self.btnSocios, self.btnPlanes, self.btnPagos,'
        )
        print("✅ Botón agregado al bucle de estilos")
        modificado = True
    
    # 5. Agregar conexión
    if 'self.btnPagos.clicked.connect' not in contenido:
        if 'self.btnPlanes.clicked.connect' in contenido:
            contenido = contenido.replace(
                'self.btnPlanes.clicked.connect(self.abrir_planes)',
                'self.btnPlanes.clicked.connect(self.abrir_planes)\n'
                '        self.btnPagos.clicked.connect(self.abrir_pagos)'
            )
            print("✅ Conexión agregada")
            modificado = True
    else:
        print("ℹ️  Conexión ya existe")
    
    # 6. Agregar método abrir_pagos
    if 'def abrir_pagos(self):' not in contenido:
        metodo_pagos = '''
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
            QMessageBox.critical(self, "Error", f"No se pudo abrir la ventana de Pagos:\\n{str(e)}")
'''
        
        # Buscar después de abrir_planes
        if 'def abrir_planes(self):' in contenido:
            # Encontrar el final del método abrir_planes
            partes = contenido.split('def abrir_planes(self):')
            if len(partes) >= 2:
                # Encontrar el siguiente def
                siguiente_def = partes[1].find('\n    def ')
                if siguiente_def > 0:
                    contenido = (partes[0] + 'def abrir_planes(self):' + 
                               partes[1][:siguiente_def] + metodo_pagos + 
                               partes[1][siguiente_def:])
                    print("✅ Método abrir_pagos agregado")
                    modificado = True
    else:
        print("ℹ️  Método abrir_pagos ya existe")
    
    # Guardar cambios si hubo modificaciones
    if modificado:
        with open('main.py', 'w', encoding='utf-8') as f:
            f.write(contenido)
        print("\n✅ Integración completada exitosamente")
        print("⚠️  IMPORTANTE: Revisá main.py para verificar que todo esté correcto")
        return True
    else:
        print("\nℹ️  No se realizaron cambios (ya estaba integrado)")
        return True


def crear_estructura_directorios():
    """Crea las carpetas necesarias si no existen."""
    carpetas = ['models', 'controllers', 'views']
    
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
            print(f"✅ Carpeta creada: {carpeta}")
            
            # Crear __init__.py para que sea un paquete de Python
            init_file = os.path.join(carpeta, '__init__.py')
            with open(init_file, 'w') as f:
                f.write(f'"""Paquete {carpeta}"""\n')
        else:
            print(f"ℹ️  Carpeta ya existe: {carpeta}")


def verificar_tabla_pagos():
    """Verifica que la tabla de pagos exista en la base de datos."""
    import sqlite3
    
    db_path = 'gimnasio.db'
    if not os.path.exists(db_path):
        print(f"⚠️  No se encontró la base de datos: {db_path}")
        print("   La tabla se creará automáticamente al iniciar la aplicación")
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar si existe la tabla pagos
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pagos'")
        if c.fetchone():
            # Verificar columnas
            c.execute("PRAGMA table_info(pagos)")
            columnas = [col[1] for col in c.fetchall()]
            
            columnas_necesarias = ['id', 'socio_id', 'monto', 'fecha_pago', 
                                  'mes_correspondiente', 'metodo_pago', 'observaciones']
            
            faltantes = [col for col in columnas_necesarias if col not in columnas]
            
            if faltantes:
                print(f"⚠️  Faltan columnas en la tabla pagos: {faltantes}")
                print("   Ejecutá: python migrate_database.py")
            else:
                print("✅ Tabla de pagos correcta")
        else:
            print("ℹ️  Tabla de pagos no existe (se creará automáticamente)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error al verificar la base de datos: {e}")
        return False


def main():
    """Función principal del script."""
    print("=" * 60)
    print("🚀 INTEGRACIÓN AUTOMÁTICA DEL MÓDULO DE PAGOS")
    print("=" * 60)
    print()
    
    # 1. Crear estructura de directorios
    print("📁 Verificando estructura de directorios...")
    crear_estructura_directorios()
    print()
    
    # 2. Verificar archivos necesarios
    print("📄 Verificando archivos necesarios...")
    if not verificar_archivos():
        print("\n❌ Faltan archivos necesarios. Por favor, creá los archivos primero.")
        return
    print()
    
    # 3. Verificar base de datos
    print("🗃️  Verificando base de datos...")
    verificar_tabla_pagos()
    print()
    
    # 4. Integrar en main.py
    print("🔧 Integrando en main.py...")
    if integrar_en_main():
        print()
        print("=" * 60)
        print("✅ ¡INTEGRACIÓN COMPLETADA!")
        print("=" * 60)
        print()
        print("📝 Próximos pasos:")
        print("   1. Revisá main.py para verificar los cambios")
        print("   2. Ejecutá: python main.py")
        print("   3. Hacé clic en el botón '💰 Pagos' en el menú")
        print()
        print("💡 Si encontrás algún error, podés restaurar el backup creado")
        print()
    else:
        print("\n❌ Hubo un error durante la integración")
        print("   Restaurá el backup y realizá la integración manualmente")


if __name__ == "__main__":
    main()