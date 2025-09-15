# crear_tablas.py
from conexion.conexion import get_connection

def crear_tablas():
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla usuarios
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        mail VARCHAR(150) NOT NULL UNIQUE
    )
    """)

    # Aquí puedes agregar más tablas de tu proyecto
    # cursor.execute("CREATE TABLE productos (...)")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tablas creadas correctamente")

if __name__ == "__main__":
    crear_tablas()
