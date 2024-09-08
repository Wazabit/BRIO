import json

from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

from frontend.classes.client import Client
from frontend.classes.database import Database
from frontend.classes.project import Project
from frontend.classes.user import User

bp = Blueprint('new_project', __name__, template_folder="../../templates/admin", url_prefix="/admin/new_project")

app = Flask(__name__)
app.db = Database()

dict_vars = {}

@bp.route('/', methods=['GET', 'POST'])
def new_project():
    global btn_login, user
    if session.get("user") is None:
        return redirect(url_for('login'))
    else:
        data = session.get("user")
        user = User(data.get("userinfo"))
        user.register_update(user, app.db)
        btn_login = True

        clients = user.get_my_clients(app.db)

        if request.method == 'POST':
            project = Project(request.form['name'], user.sub, request.form['client'])
            project.register_update(project, app.db)
            client = Client.get_client(request.form['client'], app.db)
            client.add_project(project.uuid, app.db)
            flash('Project successfully created!', 'success')

        return render_template('new_project.html',
                               session=session.get("user"),
                               btn_login=btn_login,
                               user=user,
                               clients=clients,
                               role=user.role,
                               pretty=json.dumps(session.get("user"), indent=4)

                               )
