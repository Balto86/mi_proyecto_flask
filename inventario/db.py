import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "inventario.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def crear_tabla():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()
