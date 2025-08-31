from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlite3
from .db import conectar

@dataclass
class Producto:
    id: int
    nombre: str
    cantidad: int
    precio: float

    def set_cantidad(self, nueva: int):
        if nueva < 0:
            raise ValueError("Cantidad no puede ser negativa")
        self.cantidad = nueva

    def set_precio(self, nuevo: float):
        if nuevo < 0:
            raise ValueError("Precio no puede ser negativo")
        self.precio = nuevo

class Inventario:
    def __init__(self):
        self._items: Dict[int, Producto] = {}
        self._cargar_cache()

    def _cargar_cache(self):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id, nombre, cantidad, precio FROM productos ORDER BY id")
        filas = cur.fetchall()
        for id_, nombre, cantidad, precio in filas:
            self._items[id_] = Producto(id_, nombre, cantidad, precio)
        conn.close()

    def _sync_a_db(self, p: Producto):
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT id FROM productos WHERE id=?", (p.id,))
        if cur.fetchone():
            cur.execute("UPDATE productos SET nombre=?, cantidad=?, precio=? WHERE id=?",
                        (p.nombre, p.cantidad, p.precio, p.id))
        else:
            cur.execute("INSERT INTO productos(id, nombre, cantidad, precio) VALUES(?,?,?,?)",
                        (p.id, p.nombre, p.cantidad, p.precio))
        conn.commit()
        conn.close()

    def agregar_producto(self, p: Producto):
        if p.id in self._items:
            raise ValueError("ID ya existe")
        self._items[p.id] = p
        self._sync_a_db(p)

    def eliminar_producto(self, id_producto: int):
        if id_producto not in self._items:
            raise KeyError("ID no existe")
        del self._items[id_producto]
        conn = conectar()
        cur = conn.cursor()
        cur.execute("DELETE FROM productos WHERE id=?", (id_producto,))
        conn.commit()
        conn.close()

    def actualizar_cantidad(self, id_producto: int, cantidad: int):
        p = self._items.get(id_producto)
        if not p:
            raise KeyError("ID no existe")
        p.set_cantidad(cantidad)
        self._sync_a_db(p)

    def actualizar_precio(self, id_producto: int, precio: float):
        p = self._items.get(id_producto)
        if not p:
            raise KeyError("ID no existe")
        p.set_precio(precio)
        self._sync_a_db(p)

    def buscar_por_nombre(self, texto: str) -> List[Producto]:
        texto_l = texto.lower()
        resultados = [p for p in self._items.values() if texto_l in p.nombre.lower()]
        return sorted(resultados, key=lambda x: x.nombre)

    def listar_todos(self) -> List[Producto]:
        return sorted(self._items.values(), key=lambda p: p.id)
