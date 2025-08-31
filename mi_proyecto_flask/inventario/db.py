import sqlite3
DB_NAME = "inventario.db"

def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def crear_tabla():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL CHECK(cantidad >= 0),
        precio REAL NOT NULL CHECK(precio >= 0)
    )
    """)
    conn.commit()
    conn.close()
