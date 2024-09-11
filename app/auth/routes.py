from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
from bson.objectid import ObjectId
from extensions import mongo

auth = Blueprint('auth', __name__)
bcrypt = Bcrypt()

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = mongo.db.datos_usuarios.find_one({'email': request.form['email']})
        if user and bcrypt.check_password_hash(user['password'], request.form['password']):
            session['user_id'] = str(user['_id'])
            flash('Has iniciado sesión correctamente.', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Correo electrónico o contraseña inválidos.', 'danger')
    return render_template('login.html')

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        existing_user = mongo.db.datos_usuarios.find_one({'email': request.form['email']})
        if existing_user is None:
            hashpass = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
            mongo.db.datos_usuarios.insert_one({
                'nombre': request.form['nombre'],
                'email': request.form['email'],
                'password': hashpass
            })
            flash('Registro exitoso. Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        flash('Ya existe un usuario con ese correo electrónico.', 'danger')
    return render_template('register.html')