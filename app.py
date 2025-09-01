from flask import Flask, render_template, redirect, url_for, request, flash
from inventario.models import Producto, Inventario
from forms import ProductoForm

app = Flask(__name__)
app.secret_key = "CAMBIA-ESTA-CLAVE"  # Cambia esta clave por seguridad

# Inicializar inventario
inventario = Inventario()

# ==============================
# RUTAS PRINCIPALES
# ==============================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

# ==============================
# RUTAS PRODUCTOS
# ==============================
@app.route("/productos")
def lista_productos():
    productos = inventario.listar_todos()
    return render_template("productos/lista.html", productos=productos)

@app.route("/productos/nuevo", methods=["GET", "POST"])
def nuevo_producto():
    form = ProductoForm()
    if form.validate_on_submit():
        todos = inventario.listar_todos()
        nuevo_id = (max([p.id for p in todos]) + 1) if todos else 1
        p = Producto(nuevo_id, form.nombre.data, form.cantidad.data, form.precio.data)
        try:
            inventario.agregar_producto(p)
            flash("Producto agregado", "success")
            return redirect(url_for("lista_productos"))
        except Exception as e:
            flash(str(e), "danger")
    return render_template("productos/form.html", form=form, titulo="Nuevo Producto")

@app.route("/productos/editar/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    p = next((x for x in inventario.listar_todos() if x.id == id), None)
    if not p:
        flash("Producto no encontrado", "warning")
        return redirect(url_for("lista_productos"))
    form = ProductoForm(obj=p)
    if form.validate_on_submit():
        p.nombre = form.nombre.data
        p.cantidad = form.cantidad.data
        p.precio = form.precio.data
        inventario._sync_a_db(p)
        flash("Producto actualizado", "success")
        return redirect(url_for("lista_productos"))
    return render_template("productos/form.html", form=form, titulo="Editar Producto", producto=p)

@app.route("/productos/eliminar/<int:id>", methods=["POST"])
def eliminar_producto(id):
    try:
        inventario.eliminar_producto(id)
        flash("Producto eliminado", "success")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("lista_productos"))

# ==============================
# EJECUTAR APP
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
