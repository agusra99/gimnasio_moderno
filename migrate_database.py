"""
migrate_database.py
Script para migrar y actualizar la base de datos del gimnasio.
Ejecutar UNA SOLA VEZ para actualizar la estructura de la base de datos.
"""

import sqlite3
import os


def verificar_columna_existe(cursor, tabla, columna):
    """Verifica si una columna existe en una tabla."""
    cursor.execute(f"PRAGMA table_info({tabla})")
    columnas = [info[1] for info in cursor.fetchall()]
    return columna in columnas


def migrar_base_datos():
    """Realiza la migración de la base de datos."""
    db_path = "gimnasio.db"
    
    print("🔄 Iniciando migración de base de datos...")
    
    # Crear backup
    if os.path.exists(db_path):
        import shutil
        backup_path = f"{db_path}.backup"
        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup creado: {backup_path}")
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # 1. Verificar y crear tabla de planes si no existe
    c.execute("""
        CREATE TABLE IF NOT EXISTS planes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            duracion_dias INTEGER NOT NULL
        )
    """)
    print("✓ Tabla 'planes' verificada")
    
    # 2. Verificar tabla de socios
    if not verificar_columna_existe(c, 'socios', 'plan_id'):
        print("⚠️  Agregando columna 'plan_id' a tabla socios...")
        c.execute("ALTER TABLE socios ADD COLUMN plan_id INTEGER")
        print("✓ Columna 'plan_id' agregada")
    
    if not verificar_columna_existe(c, 'socios', 'activo'):
        print("⚠️  Agregando columna 'activo' a tabla socios...")
        c.execute("ALTER TABLE socios ADD COLUMN activo INTEGER DEFAULT 1")
        print("✓ Columna 'activo' agregada")
    
    # 3. Verificar que la columna sea 'fecha_inscripcion'
    if not verificar_columna_existe(c, 'socios', 'fecha_inscripcion'):
        if verificar_columna_existe(c, 'socios', 'fecha_alta'):
            print("⚠️  Renombrando 'fecha_alta' a 'fecha_inscripcion'...")
            # SQLite no permite RENAME COLUMN directamente en versiones antiguas
            # Necesitamos recrear la tabla
            c.execute("ALTER TABLE socios RENAME TO socios_old")
            
            c.execute("""
                CREATE TABLE socios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    telefono TEXT,
                    fecha_inscripcion TEXT,
                    plan_id INTEGER,
                    activo INTEGER DEFAULT 1,
                    FOREIGN KEY(plan_id) REFERENCES planes(id)
                )
            """)
            
            c.execute("""
                INSERT INTO socios (id, nombre, apellido, telefono, fecha_inscripcion, plan_id, activo)
                SELECT id, nombre, apellido, telefono, fecha_alta, plan_id, 
                       COALESCE(activo, 1)
                FROM socios_old
            """)
            
            c.execute("DROP TABLE socios_old")
            print("✓ Tabla 'socios' actualizada con 'fecha_inscripcion'")
    
    # 4. Crear tabla de notificaciones
    c.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            leida INTEGER DEFAULT 0,
            prioridad TEXT DEFAULT 'normal',
            fecha_vencimiento TEXT,
            FOREIGN KEY(socio_id) REFERENCES socios(id)
        )
    """)
    print("✓ Tabla 'notificaciones' verificada")
    
    # 5. Verificar tabla de pagos
    c.execute("""
        CREATE TABLE IF NOT EXISTS pagos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_id INTEGER NOT NULL,
            monto REAL NOT NULL,
            fecha_pago TEXT NOT NULL,
            mes_correspondiente TEXT NOT NULL,
            FOREIGN KEY(socio_id) REFERENCES socios(id)
        )
    """)
    print("✓ Tabla 'pagos' verificada")
    
    # 6. Crear datos de ejemplo si las tablas están vacías
    c.execute("SELECT COUNT(*) FROM planes")
    if c.fetchone()[0] == 0:
        print("📝 Creando planes de ejemplo...")
        planes_ejemplo = [
            ("Mensual", 5000, 30),
            ("Trimestral", 13500, 90),
            ("Semestral", 25000, 180),
            ("Anual", 45000, 365)
        ]
        c.executemany("""
            INSERT INTO planes (nombre, precio, duracion_dias)
            VALUES (?, ?, ?)
        """, planes_ejemplo)
        print("✓ Planes de ejemplo creados")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Migración completada exitosamente!")
    print("📌 Podés ejecutar main.py ahora.")


if __name__ == "__main__":
    try:
        migrar_base_datos()
    except Exception as e:
        print(f"\n❌ Error durante la migración: {e}")
        print("Por favor, revisá el error y volvé a intentar.")