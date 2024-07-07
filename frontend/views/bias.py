import json

import os
import subprocess
from subprocess import check_output

from flask import (Blueprint, Flask, Response, current_app, flash, jsonify,
                   redirect, render_template, request, session, url_for)

from frontend.views.bias_route import FreqvsFreq, FreqvsRef
from brio.utils.funcs import allowed_file, handle_multiupload

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


@bp.route('/', methods=['GET', 'POST'])
def home_bias():
    if session.get("user") == None:
        return redirect(url_for('login'))
    else:
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
            session.clear()
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
                        current_app.config['UPLOAD_FOLDER'], dict_vars['dataset']))
                    used_df = dict_vars['dataset']
                    success_status = "text-success"
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
                        current_app.config['UPLOAD_FOLDER'], dict_vars['dataset_custom']))
                    request.files['notebook'].save(os.path.join(
                        current_app.config['UPLOAD_FOLDER'], dict_vars['notebook']))
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
                                       current_app.config['UPLOAD_FOLDER'])
                notebook_extension = dict_vars['notebook'].split('.')[1]
                match notebook_extension:
                    case 'ipynb':
                        os.system("jupyter nbconvert --to python " +
                                  os.path.join(current_app.config['UPLOAD_FOLDER'], dict_vars['notebook']))
                        note_name = dict_vars['notebook'].split('.')[0]
                        subprocess.run(["python3", os.path.join(
                            current_app.config['UPLOAD_FOLDER'], note_name + ".py")])
                    case 'py':
                        subprocess.run(["python3", os.path.join(
                            current_app.config['UPLOAD_FOLDER'], dict_vars['notebook'])])
                flash('Custom preprocessing pipeline successfully uploaded and processed!', 'success')
            animation_status = ""
            return redirect('/bias')

        return render_template('home.html',
                               session=session.get("user"),
                               btn_login=btn_login,
                               pretty=json.dumps(session.get("user"), indent=4),
                               df_used=used_df,
                               status=success_status,
                               animated=animation_status)
