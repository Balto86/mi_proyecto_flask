# Contenido del archivo: app.py
#
# Este archivo contiene la aplicación básica de Flask con dos rutas.
# Puedes ejecutarlo directamente después de instalar Flask.

from flask import Flask, render_template
import os # Necesitas importar 'os' para acceder a las variables de entorno de Render.

# 1. Crea una instancia de la aplicación Flask.
app = Flask(__name__)

# 2. Define la ruta principal (ruta raíz).
# Accede a esta ruta en http://127.0.0.1:5000/
@app.route('/')
def index():
    #return '¡Hola, mundo! Esta es la página de inicio de mi_proyecto_flask.'
    return render_template('index.html')
@app.route('/about')
def about():
    return render_template('about.html')


# 3. Define una ruta dinámica con un parámetro de nombre.
# Accede a esta ruta, por ejemplo: http://127.0.0.1:5000/usuario/David
@app.route('/usuario/<nombre>')
def usuario(nombre):
    # La f-string formatea el mensaje de bienvenida.
    return f'¡Bienvenido, {nombre}!'

# 4. Esta nueva función lista todas las rutas definidas en tu aplicación.
def list_routes():
    print("Rutas disponibles:")
    for rule in app.url_map.iter_rules():
        print(f" - {rule.endpoint}: {rule.rule}")

# 5. Inicia el servidor de desarrollo si el script se ejecuta directamente.
if __name__ == '__main__':
    # Llama a la función para listar las rutas.
    list_routes()
    # Esta línea usa el puerto de Render si está disponible, o el 5000 en tu máquina.
    # El debug=True es lo que permite la recarga automática de los cambios.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
