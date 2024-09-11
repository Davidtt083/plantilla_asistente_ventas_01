from flask import Blueprint, render_template, session, redirect, url_for
from bson.objectid import ObjectId
from extensions import mongo

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = mongo.db.datos_usuarios.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('home.html', user=user)