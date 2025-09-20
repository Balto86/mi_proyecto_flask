def crear_tablas():
    # 1. Crear una instancia de la clase DBManager
    db_manager = DBManager()
    
    # 2. Usar la instancia para llamar al método get_connection()
    conn = db_manager.get_connection()
    
    if conn:
        cursor = conn.cursor()

        # Tabla usuarios
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            mail VARCHAR(150) NOT NULL UNIQUE
        )
        """)

        conn.commit()
        cursor.close()
        db_manager.close_connection()
        print("✅ Tablas creadas correctamente")
    else:
        print("❌ No se pudo establecer la conexión a la base de datos.")

if __name__ == "__main__":
    crear_tablas()