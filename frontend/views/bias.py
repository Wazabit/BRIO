import json

import os
import subprocess
from subprocess import check_output

from dotenv import find_dotenv, load_dotenv
from os import environ as env
from flask import (Blueprint, Flask, Response, current_app, flash, jsonify,
                   redirect, render_template, request, session, url_for)

from frontend.classes.database import Database
from frontend.classes.file import File
from frontend.classes.fileStatus import FileStatus
from frontend.classes.fileType import FileType
from frontend.classes.user import User
from frontend.views.bias_route import FreqvsFreq, FreqvsRef
from brio.utils.funcs import allowed_file, handle_multiupload, upload_folder

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

bp = Blueprint('bias', __name__,
               template_folder="../templates/bias", url_prefix="/bias")
bp.register_blueprint(FreqvsFreq.bp)
bp.register_blueprint(FreqvsRef.bp)

dict_vars = {}

used_df = ""
comp_thr = ""
success_status = "text-warning"
animation_status = "animated"
ips = check_output(['hostname', '-I'])
localhost_ip = ips.decode().split(" ")[0]
print(f"localhost_ip={localhost_ip}", flush=True)
# check if this script is being run inside a docker container
# if so, then the localhost_ip will be read from an environment variable
if os.system("test -f /.dockerenv") == 0:
    print("Running inside a docker container", flush=True)
    localhost_ip = os.environ['HOST_IP']
    print(f"localhost_ip={localhost_ip}", flush=True)

app = Flask(__name__)
app.db = Database()

UPLOAD_FOLDER = os.path.abspath(env.get('UPLOAD_FOLDER'))

btn_login = False
user = False

@bp.route('/', methods=['GET', 'POST'])
def home_bias():
    global btn_login, user
    if session.get("user") is None:
        return redirect(url_for('login'))
    else:
        data = session.get("user")
        user = User(data.get("userinfo"))
        user.register_update(user, app.db)
        app.config['UPLOAD_FOLDER'] = upload_folder(UPLOAD_FOLDER, user.sub)
        btn_login = True
        global used_df
        global success_status
        global animation_status
        global dict_vars

        if request.method == 'GET' and request.args.get('reset'):
            used_df = ""
            success_status = "text-warning"
            animation_status = ""
            dict_vars = {}
            user.update_all_status_files(app.db, FileStatus.USED)
        if request.method == 'POST':
            keys = list(request.files.keys())
            uploads = [request.files[x].filename for x in keys if x != '']
            if all(x == '' for x in uploads):
                flash('No files uploaded, try again!', 'danger')
                animation_status = ""
                return redirect('/bias')
            if 'dataset' in list(request.files.keys()):
                dataframe_file = request.files['dataset']
                dict_vars['dataset'] = dataframe_file.filename
                if allowed_file(dict_vars['dataset']):
                    dataframe_file.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], dict_vars['dataset']))
                    used_df = dict_vars['dataset']
                    success_status = "text-success"
                    current_file = File(dict_vars['dataset'], user.sub, FileType.DATASET, FileStatus.IN_USE, app.config['UPLOAD_FOLDER'])
                    current_file.dbInsert(current_file, app.db)
                    flash('Dataframe successfully uploaded!', 'success')
                else:
                    flash('Unsupported dataframe format.', 'danger')
                    animation_status = ""
                    return redirect('/bias')
            if ('dataset_custom' and 'notebook') in list(request.files.keys()):
                dict_vars['dataset_custom'] = request.files['dataset_custom'].filename
                dict_vars['notebook'] = request.files['notebook'].filename
                used_df = "Custom preprocessed " + dict_vars['dataset_custom']
                success_status = "text-success"
                if allowed_file(dict_vars['notebook']) and allowed_file(dict_vars['dataset_custom']):
                    request.files['dataset_custom'].save(os.path.join(
                        app.config['UPLOAD_FOLDER'], dict_vars['dataset_custom']))
                    request.files['notebook'].save(os.path.join(
                        app.config['UPLOAD_FOLDER'], dict_vars['notebook']))
                    current_file = File(dict_vars['notebook'], user.sub, FileType.NOTEBOOK, FileStatus.IN_USE, app.config['UPLOAD_FOLDER'])
                    current_file.dbInsert(current_file, app.db)
                else:
                    used_df = ""
                    dict_vars = {}
                    session.clear()
                    success_status = "text-warning"
                    flash(
                        'Unsupported notebook or dataset format. Dataset supported types: .pkl, .csv; notebook supported types: .py, .ipynb',
                        'danger')
                    animation_status = ""
                    return redirect('/bias')
                if request.files['artifacts'].filename != '':
                    handle_multiupload(request, 'artifacts',
                                       app.config['UPLOAD_FOLDER'])

                notebook_extension = dict_vars['notebook'].split('.')[1]
                match notebook_extension:
                    case 'ipynb':
                        os.system("jupyter nbconvert --to python " +
                                  os.path.join(app.config['UPLOAD_FOLDER'], dict_vars['notebook']))
                        note_name = dict_vars['notebook'].split('.')[0]
                        subprocess.run(["python3", os.path.join(
                            app.config['UPLOAD_FOLDER'], note_name + ".py")])
                    case 'py':
                        subprocess.run(["python3", os.path.join(
                            app.config['UPLOAD_FOLDER'], dict_vars['notebook'])])

                current_file = File(dict_vars['notebook'], user.sub, FileType.ARTIFACTS, FileStatus.IN_USE, app.config['UPLOAD_FOLDER'])
                current_file.dbInsert(current_file, app.db)
                flash('Custom preprocessing pipeline successfully uploaded and processed!', 'success')
            animation_status = ""
            return redirect('/bias')

        current_file = user.get_use_file(app.db)
        filename = ''
        if current_file:
            filename = current_file["name"]

        return render_template('home.html',
                               session=session.get("user"),
                               btn_login=btn_login,
                               user=user.toJSON(),
                               role=user.role,
                               pretty=json.dumps(session.get("user"), indent=4),
                               df_used=filename,
                               status=success_status,
                               animated=animation_status)
