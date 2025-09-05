from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
import json
import csv
import os
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave-secreta-aqui'  # Cambia esto en producción

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, 'datos')
DATABASE_DIR = os.path.join(BASE_DIR, 'database')
INVENTARIO_DIR = os.path.join(BASE_DIR, 'inventario')

# Crear directorios si no existen
os.makedirs(DATOS_DIR, exist_ok=True)
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(INVENTARIO_DIR, exist_ok=True)

# Rutas de archivos
TXT_FILE = os.path.join(DATOS_DIR, 'datos.txt')
JSON_FILE = os.path.join(DATOS_DIR, 'datos.json')
CSV_FILE = os.path.join(DATOS_DIR, 'datos.csv')
DB_FILE = os.path.join(DATABASE_DIR, 'usuarios.db')
PRODUCTOS_DB = os.path.join(DATABASE_DIR, 'productos.db')

# Importar módulos de inventario
try:
    from inventario.models import Producto, Inventario
    from inventario.forms import ProductoForm
    inventario_disponible = True
except ImportError:
    inventario_disponible = False
    print("Advertencia: Módulos de inventario no disponibles")

# Inicializar base de datos de usuarios
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            edad INTEGER NOT NULL,
            pais TEXT NOT NULL,
            intereses TEXT,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Inicializar base de datos de productos
def init_productos_db():
    conn = sqlite3.connect(PRODUCTOS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ==========================
# FUNCIONES PARA PERSISTENCIA DE USUARIOS
# ==========================

def guardar_txt(datos):
    try:
        with open(TXT_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*50}\n")
            f.write(f"Registro: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            for key, value in datos.items():
                f.write(f"{key}: {value}\n")
        return True
    except Exception as e:
        print(f"Error guardando TXT: {e}")
        return False

def leer_txt():
    try:
        if os.path.exists(TXT_FILE):
            with open(TXT_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        return "No hay datos almacenados en TXT."
    except Exception as e:
        print(f"Error leyendo TXT: {e}")
        return "Error al leer archivo TXT."

def guardar_json(datos):
    try:
        data = []
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        
        data.append({
            **datos,
            'fecha_registro': datetime.now().isoformat()
        })
        
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando JSON: {e}")
        return False

def leer_json():
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"Error leyendo JSON: {e}")
        return []

def guardar_csv(datos):
    try:
        file_exists = os.path.exists(CSV_FILE)
        
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['nombre', 'email', 'edad', 'pais', 'intereses', 'fecha_registro'])
            
            writer.writerow([
                datos['nombre'],
                datos['email'],
                datos['edad'],
                datos['pais'],
                datos['intereses'],
                datetime.now().isoformat()
            ])
        return True
    except Exception as e:
        print(f"Error guardando CSV: {e}")
        return False

def leer_csv():
    try:
        datos = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    datos.append(row)
        return datos
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        return []

def guardar_db(datos):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO usuarios (nombre, email, edad, pais, intereses)
            VALUES (?, ?, ?, ?, ?)
        ''', (datos['nombre'], datos['email'], datos['edad'], datos['pais'], datos['intereses']))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Error guardando en DB: {e}")
        return False

def leer_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM usuarios ORDER BY fecha_registro DESC')
        usuarios = cursor.fetchall()
        conn.close()
        return usuarios
    except Exception as e:
        print(f"Error leyendo DB: {e}")
        return []

# ==========================
# FUNCIONES PARA PERSISTENCIA DE PRODUCTOS
# ==========================

def guardar_producto_txt(producto):
    """Guardar producto en archivo TXT"""
    try:
        productos_txt = os.path.join(DATOS_DIR, 'productos.txt')
        with open(productos_txt, 'a', encoding='utf-8') as f:
            f.write(f"{datetime.now()}: ID={producto.id}, Nombre={producto.nombre}, "
                   f"Cantidad={producto.cantidad}, Precio={producto.precio}\n")
        return True
    except Exception as e:
        print(f"Error guardando producto en TXT: {e}")
        return False

def guardar_producto_json(producto):
    """Guardar producto en archivo JSON"""
    try:
        productos_json = os.path.join(DATOS_DIR, 'productos.json')
        data = []
        if os.path.exists(productos_json):
            try:
                with open(productos_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except:
                data = []
        
        # Buscar si el producto ya existe para actualizarlo
        encontrado = False
        for i, p in enumerate(data):
            if p['id'] == producto.id:
                data[i] = {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'cantidad': producto.cantidad,
                    'precio': producto.precio,
                    'fecha_actualizacion': datetime.now().isoformat()
                }
                encontrado = True
                break
        
        # Si no existe, agregarlo
        if not encontrado:
            data.append({
                'id': producto.id,
                'nombre': producto.nombre,
                'cantidad': producto.cantidad,
                'precio': producto.precio,
                'fecha_actualizacion': datetime.now().isoformat()
            })
        
        with open(productos_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando producto en JSON: {e}")
        return False

def guardar_producto_csv(producto):
    """Guardar producto en archivo CSV"""
    try:
        productos_csv = os.path.join(DATOS_DIR, 'productos.csv')
        file_exists = os.path.exists(productos_csv)
        
        with open(productos_csv, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(['id', 'nombre', 'cantidad', 'precio', 'fecha_actualizacion'])
            
            writer.writerow([
                producto.id,
                producto.nombre,
                producto.cantidad,
                producto.precio,
                datetime.now().isoformat()
            ])
        return True
    except Exception as e:
        print(f"Error guardando producto en CSV: {e}")
        return False

def guardar_producto_db(producto):
    """Guardar producto en base de datos SQLite"""
    try:
        conn = sqlite3.connect(PRODUCTOS_DB)
        cursor = conn.cursor()
        
        # Verificar si el producto ya existe
        cursor.execute("SELECT id FROM productos WHERE id = ?", (producto.id,))
        existe = cursor.fetchone()
        
        if existe:
            # Actualizar producto existente
            cursor.execute('''
                UPDATE productos 
                SET nombre = ?, cantidad = ?, precio = ?, fecha_actualizacion = ?
                WHERE id = ?
            ''', (producto.nombre, producto.cantidad, producto.precio, datetime.now().isoformat(), producto.id))
        else:
            # Insertar nuevo producto
            cursor.execute('''
                INSERT INTO productos (id, nombre, cantidad, precio)
                VALUES (?, ?, ?, ?)
            ''', (producto.id, producto.nombre, producto.cantidad, producto.precio))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error guardando producto en DB: {e}")
        return False

# ==========================
# RUTAS DE LA APLICACIÓN - USUARIOS
# ==========================

@app.route('/')
def index():
    return render_template('formulario.html')

@app.route('/procesar', methods=['POST'])
def procesar_formulario():
    try:
        # Validar y obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        email = request.form.get('email', '').strip()
        edad_str = request.form.get('edad', '0').strip()
        pais = request.form.get('pais', '').strip()
        intereses = request.form.get('intereses', 'No especificado').strip()
        
        # Validaciones básicas
        if not nombre or not email or not edad_str or not pais:
            flash('Todos los campos obligatorios deben ser completados', 'error')
            return redirect(url_for('index'))
        
        try:
            edad = int(edad_str)
            if edad <= 0 or edad > 120:
                flash('La edad debe ser un número válido entre 1 y 120', 'error')
                return redirect(url_for('index'))
        except ValueError:
            flash('La edad debe ser un número válido', 'error')
            return redirect(url_for('index'))
        
        datos = {
            'nombre': nombre,
            'email': email,
            'edad': edad,
            'pais': pais,
            'intereses': intereses
        }
        
        # Guardar en todos los formatos
        guardar_txt(datos)
        guardar_json(datos)
        guardar_csv(datos)
        
        # Guardar en base de datos
        if not guardar_db(datos):
            flash('El email ya existe en la base de datos', 'error')
            return redirect(url_for('index'))
        
        return render_template('resultado.html', **datos)
        
    except Exception as e:
        print(f"Error en procesar_formulario: {e}")
        flash('Error interno al procesar el formulario', 'error')
        return redirect(url_for('index'))

@app.route('/ver-datos')
def ver_datos():
    usuarios = leer_db()
    return render_template('ver_datos.html', usuarios=usuarios)

@app.route('/api/datos/txt')
def api_datos_txt():
    contenido = leer_txt()
    return render_template('datos_txt.html', contenido=contenido)

@app.route('/api/datos/json')
def api_datos_json():
    datos = leer_json()
    return jsonify(datos)

@app.route('/api/datos/csv')
def api_datos_csv():
    datos = leer_csv()
    return jsonify(datos)

@app.route('/api/datos/db')
def api_datos_db():
    try:
        usuarios = leer_db()
        resultado = []
        
        for usuario in usuarios:
            resultado.append({
                'id': usuario[0],
                'nombre': usuario[1],
                'email': usuario[2],
                'edad': usuario[3],
                'pais': usuario[4],
                'intereses': usuario[5],
                'fecha_registro': usuario[6]
            })
        
        return jsonify(resultado)
    
    except Exception as e:
        print(f"Error en api_datos_db: {e}")
        return jsonify({"error": "Error al obtener datos de la base de datos"}), 500

# Alias para mantener compatibilidad con formulario.html anterior
@app.route('/api/usuarios')
def api_usuarios():
    return api_datos_db()

@app.route('/descargar/<formato>')
def descargar_datos(formato):
    try:
        if formato == 'txt':
            return send_file(TXT_FILE, as_attachment=True, download_name='datos.txt')
        elif formato == 'json':
            return send_file(JSON_FILE, as_attachment=True, download_name='datos.json')
        elif formato == 'csv':
            return send_file(CSV_FILE, as_attachment=True, download_name='datos.csv')
        else:
            flash('Formato no válido', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error descargando {formato}: {e}")
        flash(f'Error al descargar el archivo {formato}', 'error')
        return redirect(url_for('index'))

# ==========================
# RUTAS DE LA APLICACIÓN - PRODUCTOS
# ==========================

@app.route('/productos')
def lista_productos():
    if not inventario_disponible:
        flash('Módulo de inventario no disponible', 'error')
        return redirect(url_for('index'))
    
    try:
        inventario = Inventario()
        productos = inventario.listar_todos()
        return render_template('productos/lista.html', productos=productos)
    except Exception as e:
        print(f"Error en lista_productos: {e}")
        flash('Error al cargar los productos', 'error')
        return redirect(url_for('index'))

@app.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if not inventario_disponible:
        flash('Módulo de inventario no disponible', 'error')
        return redirect(url_for('index'))
    
    form = ProductoForm()
    if form.validate_on_submit():
        try:
            inventario = Inventario()
            todos = inventario.listar_todos()
            nuevo_id = (max([p.id for p in todos]) + 1) if todos else 1
            
            producto = Producto(nuevo_id, form.nombre.data, form.cantidad.data, form.precio.data)
            inventario.agregar_producto(producto)
            
            # Guardar en todos los sistemas de persistencia
            guardar_producto_txt(producto)
            guardar_producto_json(producto)
            guardar_producto_csv(producto)
            guardar_producto_db(producto)
            
            flash('Producto agregado correctamente', 'success')
            return redirect(url_for('lista_productos'))
        except Exception as e:
            flash(f'Error al agregar producto: {str(e)}', 'error')
    
    return render_template('productos/form.html', form=form, titulo="Nuevo Producto")

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    if not inventario_disponible:
        flash('Módulo de inventario no disponible', 'error')
        return redirect(url_for('index'))
    
    try:
        inventario = Inventario()
        producto = next((p for p in inventario.listar_todos() if p.id == id), None)
        
        if not producto:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('lista_productos'))
        
        form = ProductoForm(obj=producto)
        
        if form.validate_on_submit():
            producto.nombre = form.nombre.data
            producto.cantidad = form.cantidad.data
            producto.precio = form.precio.data
            
            inventario._sync_a_db(producto)
            
            # Actualizar en todos los sistemas de persistencia
            guardar_producto_txt(producto)
            guardar_producto_json(producto)
            guardar_producto_csv(producto)
            guardar_producto_db(producto)
            
            flash('Producto actualizado correctamente', 'success')
            return redirect(url_for('lista_productos'))
        
        return render_template('productos/form.html', form=form, titulo="Editar Producto", producto=producto)
    
    except Exception as e:
        flash(f'Error al editar producto: {str(e)}', 'error')
        return redirect(url_for('lista_productos'))

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    if not inventario_disponible:
        flash('Módulo de inventario no disponible', 'error')
        return redirect(url_for('index'))
    
    try:
        inventario = Inventario()
        inventario.eliminar_producto(id)
        
        # También deberías eliminar de los sistemas de persistencia
        # (esto requiere funciones adicionales de eliminación)
        
        flash('Producto eliminado correctamente', 'success')
    except Exception as e:
        flash(f'Error al eliminar producto: {str(e)}', 'error')
    
    return redirect(url_for('lista_productos'))

# ==========================
# RUTAS ADICIONALES
# ==========================

@app.route('/about')
def about():
    return render_template('about.html')

# Inicializar la aplicación
if __name__ == '__main__':
    init_db()
    init_productos_db()
    print("Bases de datos inicializadas correctamente")
    print("Ejecutando aplicación en http://localhost:5000")
    app.run(debug=True, port=5000)