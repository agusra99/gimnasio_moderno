import sqlite3

DB_PATH = "gimnasio.db"

SQL = """
CREATE VIEW IF NOT EXISTS vista_vencimientos AS
SELECT 
    s.id AS socio_id,
    s.nombre,
    s.apellido,
    s.telefono,
    p.fecha_pago,
    pl.duracion_dias,
    DATE(p.fecha_pago, '+' || pl.duracion_dias || ' days') AS fecha_vencimiento
FROM pagos p
JOIN socios s ON s.id = p.socio_id
JOIN planes pl ON pl.id = s.plan_id
WHERE s.activo = 1;
"""

def crear_vista():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(SQL)
        conn.commit()
        print("Vista 'vista_vencimientos' creada o ya existente.")
    except Exception as e:
        print(f"Error al crear la vista: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    crear_vista()
