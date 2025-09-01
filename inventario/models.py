from inventario.db import get_connection, crear_tabla

class Producto:
    def __init__(self, id, nombre, cantidad, precio):
        self.id = id
        self.nombre = nombre
        self.cantidad = cantidad
        self.precio = precio

class Inventario:
    def __init__(self):
        crear_tabla()
        self._cache = []
        self._cargar_cache()

    def _cargar_cache(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, cantidad, precio FROM productos ORDER BY id")
        filas = cur.fetchall()
        self._cache = [Producto(*fila) for fila in filas]
        conn.close()

    def listar_todos(self):
        return self._cache

    def agregar_producto(self, producto):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
            (producto.nombre, producto.cantidad, producto.precio)
        )
        conn.commit()
        producto.id = cur.lastrowid
        conn.close()
        self._cache.append(producto)

    def _sync_a_db(self, producto):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id=?",
            (producto.nombre, producto.cantidad, producto.precio, producto.id)
        )
        conn.commit()
        conn.close()

    def eliminar_producto(self, id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id=?", (id,))
        conn.commit()
        conn.close()
        self._cache = [p for p in self._cache if p.id != id]
 # ==========================
    # MÉTODOS NUEVOS
    # ==========================
    def buscar_por_nombre(self, nombre):
        """Busca productos que contengan el nombre"""
        return [p for p in self._cache if nombre.lower() in p.nombre.lower()]

    def actualizar_producto(self, id, cantidad=None, precio=None):
        """Actualiza un producto existente"""
        for producto in self._cache:
            if producto.id == id:
                if cantidad is not None:
                    producto.cantidad = cantidad
                if precio is not None:
                    producto.precio = precio
                self._sync_a_db(producto)
                return True
        return False

    def mostrar_todos(self):
        """Imprime todos los productos en consola"""
        if self._cache:
            for p in self._cache:
                print(f"[{p.id}] {p.nombre} - Cantidad: {p.cantidad} - Precio: {p.precio}")
        else:
            print("📦 Inventario vacío.")