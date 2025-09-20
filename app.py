# Importaciones necesarias
import os
import io
import csv
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'clave-secreta-aqui')

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATOS_DIR = os.path.join(BASE_DIR, 'datos')

# Crear directorios si no existen
os.makedirs(DATOS_DIR, exist_ok=True)

# Rutas de archivos
TXT_FILE = os.path.join(DATOS_DIR, 'datos.txt')
JSON_FILE = os.path.join(DATOS_DIR, 'datos.json')
CSV_FILE = os.path.join(DATOS_DIR, 'datos.csv')

# Clase para gestionar la conexión a MySQL
class DBManager:
    def __init__(self):
        self.conn = None

    def get_connection(self):
        try:
            self.conn = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DB"),
                port=int(os.getenv("MYSQL_PORT", 3306))
            )
            return self.conn
        except mysql.connector.Error as err:
            print(f"Error de conexión a MySQL: {err}")
            return None

    def close_connection(self):
        if self.conn and self.conn.is_connected():
            self.conn.close()

db_manager = DBManager()

# Modelo de Usuario para Flask-Login
class User(UserMixin):
    def __init__(self, id_usuario, nombre, mail, fecha_registro):
        self.id = id_usuario
        self.nombre = nombre
        self.mail = mail
        self.fecha_registro = fecha_registro

    @staticmethod
    def get(user_id):
        conn = db_manager.get_connection()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (user_id,))
                user_data = cursor.fetchone()
                if user_data:
                    return User(
                        id_usuario=user_data['id_usuario'],
                        nombre=user_data['nombre'],
                        mail=user_data['mail'],
                        fecha_registro=user_data['fecha_registro']
                    )
            except Error as e:
                print(f"Error obteniendo usuario: {e}")
            finally:
                db_manager.close_connection()
        return None

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Función para crear tablas si no existen
def create_mysql_tables():
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    mail VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255) NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS producto (
                    id_producto INT AUTO_INCREMENT PRIMARY KEY,
                    nombre VARCHAR(255) NOT NULL,
                    costo DECIMAL(10, 2) NOT NULL,
                    descripcion TEXT,
                    stock INT NOT NULL DEFAULT 0
                )
            """)
            conn.commit()
            cursor.close()
            db_manager.close_connection()
            print("✅ Tablas verificadas/creadas correctamente.")
    except Error as e:
        print(f"❌ Error al crear tablas: {e}")

def guardar_mysql_db(datos):
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO usuarios (nombre, mail, password)
                VALUES (%s, %s, %s)
            ''', (datos['nombre'], datos['mail'], generate_password_hash(datos['password'])))
            conn.commit()
            cursor.close()
            db_manager.close_connection()
            return True
    except Error as e:
        print(f"Error guardando en MySQL: {e}")
        return False

def verificar_usuario(mail, password):
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE mail = %s", (mail,))
            user_data = cursor.fetchone()
            cursor.close()
            db_manager.close_connection()
            
            if user_data and check_password_hash(user_data['password'], password):
                return User(
                    id_usuario=user_data['id_usuario'],
                    nombre=user_data['nombre'],
                    mail=user_data['mail'],
                    fecha_registro=user_data['fecha_registro']
                )
    except Error as e:
        print(f"Error verificando usuario: {e}")
    return None

# Funciones para persistencia de datos (mantienen la lógica original)
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
                data = json.load(f)
                # Ordenar los datos por fecha_registro descendente
                return sorted(data, key=lambda x: x.get('fecha_registro', ''), reverse=True)
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
                writer.writerow(['nombre', 'mail', 'edad', 'pais', 'intereses', 'fecha_registro'])
            
            writer.writerow([
                datos['nombre'],
                datos['mail'],
                datos.get('edad', ''),
                datos.get('pais', ''),
                datos.get('intereses', ''),
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
            # Ordenar los datos por fecha_registro descendente
            return sorted(datos, key=lambda x: x.get('fecha_registro', ''), reverse=True)
        return []
    except Exception as e:
        print(f"Error leyendo CSV: {e}")
        return []


# ==========================
# RUTAS DE AUTENTICACIÓN
# ==========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        mail = request.form.get('mail')
        password = request.form.get('password')
        
        user = verificar_usuario(mail, password)
        if user:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('Credenciales inválidas. Por favor, intenta de nuevo.', 'error')
    
    return render_template('auth/login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        mail = request.form.get('mail')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('auth/registro.html')
        
        try:
            conn = db_manager.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_usuario FROM usuarios WHERE mail = %s", (mail,))
                if cursor.fetchone():
                    flash('El correo electrónico ya está registrado.', 'error')
                    return render_template('auth/registro.html')
                cursor.close()
                db_manager.close_connection()
        except Error as e:
            print(f"Error verificando usuario existente: {e}")
        
        datos = {
            'nombre': nombre,
            'mail': mail,
            'password': password
        }
        
        if guardar_mysql_db(datos):
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error en el registro. Por favor, intenta de nuevo.', 'error')
    
    return render_template('auth/registro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# ==========================
# RUTA ÚNICA DEL DASHBOARD (CONSOLIDADA)
# ==========================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    datos_dashboard = {}
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Datos de Usuarios (MySQL)
            cursor.execute("SELECT id_usuario, nombre, mail, fecha_registro FROM usuarios ORDER BY fecha_registro DESC")
            datos_dashboard['usuarios'] = cursor.fetchall()
            
            # Datos de Productos (MySQL)
            cursor.execute("SELECT * FROM producto ORDER BY nombre")
            datos_dashboard['productos'] = cursor.fetchall()
            
            cursor.close()
            db_manager.close_connection()
            
        # Leer datos de los archivos locales (ahora ordenados dentro de las funciones)
        datos_dashboard['datos_txt'] = leer_txt()
        datos_dashboard['datos_json'] = leer_json()
        datos_dashboard['datos_csv'] = leer_csv()
            
        return render_template('auth/dashboard.html', **datos_dashboard)
    
    except Error as e:
        print(f"Error al cargar el dashboard: {e}")
        flash('Error al cargar la información del dashboard.', 'error')
        # Retorna un dashboard con datos vacíos en caso de error
        return render_template('auth/dashboard.html', 
                             usuarios=[], 
                             productos=[], 
                             datos_txt="Error al cargar.", 
                             datos_json=[], 
                             datos_csv=[])

# ==========================
# RUTAS DE ACCIÓN PARA EL DASHBOARD
# ==========================

@app.route('/procesar', methods=['POST'])
@login_required
def procesar_formulario():
    try:
        nombre = request.form.get('nombre', '').strip()
        mail = request.form.get('mail', '').strip()
        edad_str = request.form.get('edad', '0').strip()
        pais = request.form.get('pais', '').strip()
        intereses = request.form.get('intereses', 'No especificado').strip()
        
        if not nombre or not mail or not edad_str or not pais:
            flash('Todos los campos obligatorios deben ser completados', 'error')
            return redirect(url_for('dashboard'))
        
        try:
            edad = int(edad_str)
            if edad <= 0 or edad > 120:
                flash('La edad debe ser un número válido entre 1 y 120', 'error')
                return redirect(url_for('dashboard'))
        except ValueError:
            flash('La edad debe ser un número válido', 'error')
            return redirect(url_for('dashboard'))
        
        datos = {
            'nombre': nombre,
            'mail': mail,
            'edad': edad,
            'pais': pais,
            'intereses': intereses
        }
        
        guardar_txt(datos)
        guardar_json(datos)
        guardar_csv(datos)
        
        flash('Datos procesados correctamente', 'success')
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        print(f"Error en procesar_formulario: {e}")
        flash('Error interno al procesar el formulario', 'error')
        return redirect(url_for('dashboard'))

# Rutas para productos
@app.route('/productos/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_producto():
    if request.method == 'POST':
        try:
            nombre = request.form.get('nombre')
            costo = request.form.get('costo')
            descripcion = request.form.get('descripcion')
            stock = request.form.get('stock')
            
            conn = db_manager.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO producto (nombre, costo, descripcion, stock)
                    VALUES (%s, %s, %s, %s)
                ''', (nombre, costo, descripcion, stock))
                conn.commit()
                cursor.close()
                db_manager.close_connection()
                
                flash('Producto agregado correctamente', 'success')
                return redirect(url_for('dashboard'))
        except Error as e:
            print(f"Error agregando producto: {e}")
            flash('Error al agregar el producto', 'error')
    
    return render_template('productos/form.html', titulo="Nuevo Producto")

@app.route('/productos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_producto(id):
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            if request.method == 'POST':
                nombre = request.form.get('nombre')
                costo = request.form.get('costo')
                descripcion = request.form.get('descripcion')
                stock = request.form.get('stock')
                
                cursor.execute('''
                    UPDATE producto 
                    SET nombre = %s, costo = %s, descripcion = %s, stock = %s
                    WHERE id_producto = %s
                ''', (nombre, costo, descripcion, stock, id))
                conn.commit()
                
                flash('Producto actualizado correctamente', 'success')
                return redirect(url_for('dashboard'))
            else:
                cursor.execute("SELECT * FROM producto WHERE id_producto = %s", (id,))
                producto = cursor.fetchone()
                cursor.close()
                db_manager.close_connection()
                
                if producto:
                    return render_template('productos/form.html', titulo="Editar Producto", producto=producto)
                else:
                    flash('Producto no encontrado', 'error')
                    return redirect(url_for('dashboard'))
    except Error as e:
        print(f"Error editando producto: {e}")
        flash('Error al editar el producto', 'error')
        return redirect(url_for('dashboard'))

@app.route('/productos/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar_producto(id):
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
            conn.commit()
            cursor.close()
            db_manager.close_connection()
            
            flash('Producto eliminado correctamente', 'success')
    except Error as e:
        print(f"Error eliminando producto: {e}")
        flash('Error al eliminar el producto', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/eliminar_producto/<int:id>', methods=['POST'])
@login_required
def eliminar_producto_dashboard(id):
    try:
        conn = db_manager.get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id,))
            conn.commit()
            cursor.close()
            db_manager.close_connection()
            
            flash('Producto eliminado correctamente', 'success')
    except Error as e:
        print(f"Error eliminando producto: {e}")
        flash('Error al eliminar el producto', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/descargar/<formato>')
@login_required
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
            return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"Error descargando {formato}: {e}")
        flash(f'Error al descargar el archivo {formato}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/perfil')
@login_required
def perfil():
    return render_template('auth/perfil.html', usuario=current_user)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/health')
def health_check():
    conn = db_manager.get_connection()
    mysql_status = "✅ Conectado" if conn else "❌ No conectado"
    if conn: 
        conn.close()
    
    info = {
        "status": "ok",
        "mysql_status": mysql_status,
        "timestamp": datetime.now().isoformat()
    }
    return jsonify(info)

@app.route('/test_db')
def test_db():
    conn = db_manager.get_connection()
    if conn:
        conn.close()
        return "✅ ¡Conexión a la base de datos MySQL exitosa!"
    else:
        return "❌ Error al conectar a la base de datos MySQL."

if __name__ == '__main__':
    print("🔄 Inicializando base de datos MySQL...")
    create_mysql_tables()
    
    print("\n🎯 URLs importantes:")
    print("   http://localhost:5000/login - Iniciar sesión")
    print("   http://localhost:5000/registro - Registrarse")
    print("   http://localhost:5000/ - Dashboard principal")
    print("\n🚀 Servidor iniciando...")
    
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000,
        use_reloader=False,
        threaded=True
    )