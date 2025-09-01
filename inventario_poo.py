import sqlite3

# ==========================
# Clase Producto
# ==========================
class Producto:
    def __init__(self, id_producto, nombre, cantidad, precio):
        self.id = id_producto
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

    def __str__(self):
        return f"ID: {self.id}, Nombre: {self.nombre}, Cantidad: {self.cantidad}, Precio: {self.precio}"


# ==========================
# Clase Inventario
# ==========================
class Inventario:
    def __init__(self):
        self.productos = {}  # Diccionario para acceso rápido por ID
        self.conn = sqlite3.connect("inventario.db")
        self.cursor = self.conn.cursor()
        self.crear_tabla()

    def crear_tabla(self):
        """Crea la tabla productos si no existe"""
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            nombre TEXT NOT NULL,
                            cantidad INTEGER NOT NULL,
                            precio REAL NOT NULL)''')
        self.conn.commit()

    def cargar_desde_bd(self):
        """Carga los productos existentes desde la BD al diccionario"""
        self.cursor.execute("SELECT * FROM productos")
        filas = self.cursor.fetchall()
        for fila in filas:
            id_producto, nombre, cantidad, precio = fila
            self.productos[id_producto] = Producto(id_producto, nombre, cantidad, precio)

    def agregar_producto(self, nombre, cantidad, precio):
        """Agrega un producto nuevo"""
        self.cursor.execute("INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
                            (nombre, cantidad, precio))
        self.conn.commit()
        id_producto = self.cursor.lastrowid
        self.productos[id_producto] = Producto(id_producto, nombre, cantidad, precio)
        print("✅ Producto agregado correctamente.")

    def eliminar_producto(self, id_producto):
        """Elimina un producto por ID"""
        if id_producto in self.productos:
            self.cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            self.conn.commit()
            del self.productos[id_producto]
            print("🗑️ Producto eliminado correctamente.")
        else:
            print("⚠️ Producto no encontrado.")

    def actualizar_producto(self, id_producto, cantidad=None, precio=None):
        """Actualiza cantidad y/o precio de un producto"""
        if id_producto in self.productos:
            producto = self.productos[id_producto]
            if cantidad is not None:
                producto.cantidad = cantidad
            if precio is not None:
                producto.precio = precio

            self.cursor.execute("UPDATE productos SET cantidad = ?, precio = ? WHERE id = ?",
                                (producto.cantidad, producto.precio, id_producto))
            self.conn.commit()
            print("✏️ Producto actualizado correctamente.")
        else:
            print("⚠️ Producto no encontrado.")

    def buscar_producto(self, nombre):
        """Busca productos por nombre"""
        encontrados = [p for p in self.productos.values() if nombre.lower() in p.nombre.lower()]
        if encontrados:
            for p in encontrados:
                print(p)
        else:
            print("⚠️ No se encontraron productos con ese nombre.")

    def mostrar_todos(self):
        """Muestra todos los productos"""
        if self.productos:
            for p in self.productos.values():
                print(p)
        else:
            print("📦 No hay productos en el inventario.")


# ==========================
# Menú interactivo
# ==========================
def menu():
    inventario = Inventario()
    inventario.cargar_desde_bd()

    while True:
        print("\n📋 --- Menú de Inventario ---")
        print("1. Agregar producto")
        print("2. Eliminar producto")
        print("3. Actualizar producto")
        print("4. Buscar producto")
        print("5. Mostrar todos los productos")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre del producto: ")
            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: "))
            inventario.agregar_producto(nombre, cantidad, precio)

        elif opcion == "2":
            id_producto = int(input("ID del producto a eliminar: "))
            inventario.eliminar_producto(id_producto)

        elif opcion == "3":
            id_producto = int(input("ID del producto a actualizar: "))
            cantidad = input("Nueva cantidad (dejar vacío para no cambiar): ")
            precio = input("Nuevo precio (dejar vacío para no cambiar): ")

            cantidad = int(cantidad) if cantidad else None
            precio = float(precio) if precio else None

            inventario.actualizar_producto(id_producto, cantidad, precio)

        elif opcion == "4":
            nombre = input("Ingrese el nombre a buscar: ")
            inventario.buscar_producto(nombre)

        elif opcion == "5":
            inventario.mostrar_todos()

        elif opcion == "6":
            print("👋 Saliendo del sistema...")
            break

        else:
            print("⚠️ Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    menu()
