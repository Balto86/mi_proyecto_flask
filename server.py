from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'una_clave_secreta_muy_segura' # Cambia esto por una clave real

# Esta es la página principal
@app.route('/')
def home():
    return "<h1>¡Hola! ¡El servidor está funcionando!</h1><p>Intenta ir a las siguientes páginas:</p><ul><li><a href='/registro'>Registro</a></li><li><a href='/login'>Login</a></li></ul>"

# RUTA: Registro de usuario
@app.route('/registro')
def registro():
    return render_template('registro.html')

# RUTA: Inicio de sesión
@app.route('/login')
def login():
    return render_template('login.html')

# RUTA: Página protegida (solo para usuarios logueados)
@app.route('/protegida')
def protegida():
    if 'usuario' in session:
        return render_template('protegida.html', usuario=session['usuario'])
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)