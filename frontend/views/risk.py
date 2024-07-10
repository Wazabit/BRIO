import json
import os

from dotenv import find_dotenv, load_dotenv
from os import environ as env
from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

from brio.utils.funcs import upload_folder
from frontend.classes.database import Database
from frontend.classes.user import User
from frontend.classes.analysis import Analysis

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

bp = Blueprint('risk', __name__, template_folder="../templates/risk", url_prefix="/risk")

dict_vars = {}

used_df = ""
comp_thr = ""
success_status = "text-warning"
animation_status = "animated"

app = Flask(__name__)
app.db = Database()

UPLOAD_FOLDER = os.path.abspath(env.get('UPLOAD_FOLDER'))

btn_login = False
user = False




@bp.route('/', methods=['GET'])
def risk_home():
    global btn_login, user
    if session.get("user") is None:
        return redirect(url_for('login'))
    else:
        data = session.get("user")
        user = User(data.get("userinfo"))
        user.register_update(user, current_app.db)
        app.config['UPLOAD_FOLDER'] = upload_folder(UPLOAD_FOLDER, user.sub)
        btn_login = True

    analysis = Analysis.getAnalysis(user.sub, app.db)
    return render_template('risk_home.html',
                           session=session.get("user"),
                           btn_login=btn_login,
                           user=user.toJSON(),
                           analysis=analysis,
                           pretty=json.dumps(session.get("user"), indent=4),
                           status=success_status,
                           animated=animation_status)
