"""
fix_pagos_table.py
Script para agregar las columnas faltantes a la tabla pagos.
Ejecutar UNA SOLA VEZ para actualizar la estructura.
"""

import sqlite3
import os
from datetime import datetime


def verificar_columna_existe(cursor, tabla, columna):
    """Verifica si una columna existe en una tabla."""
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [info[1] for info in cursor.fetchall()]
    return columna in columnas


def actualizar_tabla_pagos():
    """Actualiza la tabla pagos agregando las columnas faltantes."""
    db_path = "gimnasio.db"
    
    if not os.path.exists(db_path):
        print("❌ No se encontró la base de datos gimnasio.db")
        return False
    
    print("=" * 60)
    print("🔧 ACTUALIZANDO TABLA DE PAGOS")
    print("=" * 60)
    print()
    
    # Crear backup
    import shutil
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup creado: {backup_path}")
    print()
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # Verificar si existen las columnas
        tiene_metodo = verificar_columna_existe(c, 'pagos', 'metodo_pago')
        tiene_observaciones = verificar_columna_existe(c, 'pagos', 'observaciones')
        
        print("📊 Estado actual de la tabla pagos:")
        c.execute("PRAGMA table_info(pagos)")
        columnas = c.fetchall()
        for col in columnas:
            print(f"   - {col[1]} ({col[2]})")
        print()
        
        # Agregar columnas si no existen
        if not tiene_metodo:
            print("➕ Agregando columna 'metodo_pago'...")
            c.execute("""
                ALTER TABLE pagos 
                ADD COLUMN metodo_pago TEXT DEFAULT 'efectivo'
            """)
            print("✅ Columna 'metodo_pago' agregada")
        else:
            print("ℹ️  Columna 'metodo_pago' ya existe")
        
        if not tiene_observaciones:
            print("➕ Agregando columna 'observaciones'...")
            c.execute("""
                ALTER TABLE pagos 
                ADD COLUMN observaciones TEXT
            """)
            print("✅ Columna 'observaciones' agregada")
        else:
            print("ℹ️  Columna 'observaciones' ya existe")
        
        conn.commit()
        
        # Verificar estructura final
        print()
        print("📊 Estructura final de la tabla pagos:")
        c.execute("PRAGMA table_info(pagos)")
        columnas = c.fetchall()
        for col in columnas:
            print(f"   ✓ {col[1]} ({col[2]})")
        
        # Actualizar registros existentes sin método
        c.execute("""
            UPDATE pagos 
            SET metodo_pago = 'efectivo' 
            WHERE metodo_pago IS NULL
        """)
        conn.commit()
        
        print()
        print("=" * 60)
        print("✅ ¡ACTUALIZACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print()
        print("📌 Ahora podés ejecutar main.py sin problemas")
        print()
        
        conn.close()
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {e}")
        print("=" * 60)
        print()
        print(f"💡 Podés restaurar el backup desde: {backup_path}")
        return False


if __name__ == "__main__":
    try:
        actualizar_tabla_pagos()
        input("\nPresioná ENTER para salir...")
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        input("\nPresioná ENTER para salir...")
        