from flask import Flask, render_template, redirect, url_for, request, flash
from inventario.db import crear_tabla
from inventario.models import Producto, Inventario
from forms import ProductoForm

app = Flask(__name__)
app.secret_key = "CAMBIA-ESTA-CLAVE"

# Inicializar DB y dominio
crear_tabla()
inventario = Inventario()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/productos")
def lista_productos():
    productos = inventario.listar_todos()
    return render_template("productos/lista.html", productos=productos)

@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        # Generar ID único: busca el mayor y suma 1
        todos = inventario.listar_todos()
        nuevo_id = (max([p.id for p in todos]) + 1) if todos else 1
        producto = Producto(nuevo_id, form.nombre.data, int(form.cantidad.data), float(form.precio.data))
        try:
            inventario.agregar_producto(producto)
            flash("Producto agregado", "success")
            return redirect(url_for("lista_productos"))
        except Exception as e:
            flash(str(e), "danger")
    return render_template("productos/form.html", form=form, titulo="Nuevo Producto")

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    # obtener producto
    productos = inventario.listar_todos()
    p = next((x for x in productos if x.id == id), None)
    if not p:
        flash("Producto no encontrado", "warning")
        return redirect(url_for("lista_productos"))
    form = ProductoForm(obj=p)
    if form.validate_on_submit():
        try:
            inventario.actualizar_cantidad(id, int(form.cantidad.data))
            inventario.actualizar_precio(id, float(form.precio.data))
            # actualizar nombre manualmente en cache y BD
            p.nombre = form.nombre.data
            inventario._sync_a_db(p)  # método interno (si no quieres usar, crea método público)
            flash("Producto actualizado", "success")
            return redirect(url_for("lista_productos"))
        except Exception as e:
            flash(str(e), "danger")
    return render_template("productos/form.html", form=form, titulo="Editar Producto", producto=p)

@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    try:
        inventario.eliminar_producto(id)
        flash("Producto eliminado", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("lista_productos"))

if __name__ == "__main__":
    app.run(debug=True)
