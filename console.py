from inventario.models import Inventario, Producto

def menu():
    inventario = Inventario()

    while True:
        print("\n📋 --- Menú de Inventario ---")
        print("1. Agregar producto")
        print("2. Eliminar producto")
        print("3. Actualizar producto")
        print("4. Buscar producto")
        print("5. Mostrar todos")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            nombre = input("Nombre del producto: ")
            cantidad = int(input("Cantidad: "))
            precio = float(input("Precio: "))
            inventario.agregar_producto(Producto(None, nombre, cantidad, precio))
            print("✅ Producto agregado.")

        elif opcion == "2":
            id = int(input("ID del producto a eliminar: "))
            inventario.eliminar_producto(id)
            print("🗑️ Producto eliminado.")

        elif opcion == "3":
            id = int(input("ID del producto a actualizar: "))
            cantidad = input("Nueva cantidad (enter para omitir): ")
            precio = input("Nuevo precio (enter para omitir): ")

            cantidad = int(cantidad) if cantidad else None
            precio = float(precio) if precio else None

            if inventario.actualizar_producto(id, cantidad, precio):
                print("✏️ Producto actualizado.")
            else:
                print("⚠️ Producto no encontrado.")

        elif opcion == "4":
            nombre = input("Ingrese el nombre a buscar: ")
            encontrados = inventario.buscar_por_nombre(nombre)
            if encontrados:
                for p in encontrados:
                    print(f"[{p.id}] {p.nombre} - Cantidad: {p.cantidad}, Precio: {p.precio}")
            else:
                print("⚠️ No se encontraron productos.")

        elif opcion == "5":
            inventario.mostrar_todos()

        elif opcion == "6":
            print("👋 Saliendo del sistema...")
            break

        else:
            print("⚠️ Opción inválida.")

if __name__ == "__main__":
    menu()
