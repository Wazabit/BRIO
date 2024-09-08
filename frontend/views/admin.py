import json
import os

from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app
from os import environ as env
from brio.utils.funcs import upload_folder
from frontend.classes.database import Database
from frontend.classes.user import User

bp = Blueprint('admin', __name__, template_folder="../templates/admin", url_prefix="/admin")

app = Flask(__name__)
app.db = Database()

UPLOAD_FOLDER = os.path.abspath(env.get('UPLOAD_FOLDER'))

@bp.route('/', methods=['GET'])
def admin_home():
    global btn_login, user
    if session.get("user") is None:
        return redirect(url_for('login'))
    else:
        data = session.get("user")
        user = User(data.get("userinfo"))
        user.register_update(user, app.db)
        app.config['UPLOAD_FOLDER'] = upload_folder(UPLOAD_FOLDER, user.sub)
        btn_login = True

        clients = user.get_my_clients(app.db)
        # flash(clients, 'success')

        return render_template('admin/admin_home.html',
                                   session=session.get("user"),
                                   btn_login=btn_login,
                                   user=user,
                                   clients=clients,
                                   role=user.role,
                                   pretty=json.dumps(session.get("user"), indent=4)
                               )
