import hashlib
import json
import os
import uuid

from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, \
    current_app
from os import environ as env
from brio.utils.funcs import upload_folder, allowed_file_logo, get_file_extension
from frontend.classes.client import Client

from frontend.classes.database import Database
from frontend.classes.user import User

bp = Blueprint('new_client', __name__, template_folder="../../templates/admin", url_prefix="/admin/new_client")

app = Flask(__name__)
app.db = Database()

dict_vars = {}

UPLOAD_FOLDER = os.path.abspath(env.get('UPLOAD_FOLDER'))


@bp.route('/', methods=['GET', 'POST'])
def new_client():
    global btn_login, user
    if session.get("user") is None:
        return redirect(url_for('login'))
    else:
        data = session.get("user")
        user = User(data.get("userinfo"))
        user.register_update(user, app.db)
        app.config['UPLOAD_FOLDER'] = upload_folder(UPLOAD_FOLDER, 'client_logos')
        btn_login = True

    if request.method == 'GET':
        admins = user.get_users_by_role(app.db, "Admin")
        editors = user.get_users_by_role(app.db, "Editor")
        return render_template('new_client.html',
                               session=session.get("user"),
                               btn_login=btn_login,
                               user=user,
                               admins=admins,
                               editors=editors,
                               role=user.role,
                               pretty=json.dumps(session.get("user"), indent=4)

                               )
    else:
        keys = list(request.files.keys())
        uploads = [request.files[x].filename for x in keys if x != '']
        if all(x == '' for x in uploads):
            flash('No logo uploaded, try again!', 'danger')
            return redirect('/admin/new_client')
        if 'logo' in list(request.files.keys()):
            logo_file = request.files['logo']
            ext = get_file_extension(logo_file.filename)
            dict_vars['logo'] = hashlib.md5(str(uuid.uuid4().hex[:16].lower()).encode('utf-8')).hexdigest() + "." + ext
            logo_file.save(os.path.join(app.config['UPLOAD_FOLDER'], dict_vars['logo']))

            if allowed_file_logo(dict_vars['logo']):
                client = Client(
                    request.form['name'],
                    request.form['contact'],
                    request.form['email'],
                    "/client_logos/" + dict_vars['logo'],
                    user.sub,
                    request.form['admins'],
                    request.form['editors'],
                    []
                )

                client.register_update(client, app.db)
                flash('Client successfully created!', 'success')

            else:
                flash('Unsupported logo format.', 'danger')
                return redirect('/admin/new_client')

        return render_template('new_client.html',
                               session=session.get("user"),
                               btn_login=btn_login,
                               user=user.toJSON(),
                               role=user.role,
                               pretty=json.dumps(session.get("user"), indent=4)
                               )
