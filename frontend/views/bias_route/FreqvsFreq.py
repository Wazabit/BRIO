import glob
import os
import pickle
from statistics import mean, stdev
from subprocess import check_output

import pandas as pd
from flask import (Blueprint, current_app, flash, jsonify,
                   redirect, render_template, request)

from brio.bias.FreqVsFreqBiasDetector import FreqVsFreqBiasDetector
from brio.utils.funcs import order_violations

bp = Blueprint('FreqvsFreq', __name__,
               template_folder="../../templates/bias", url_prefix="/freqvsfreq")

dict_vars = {}
agg_funcs = {
    'min': min,
    'max': max,
    'mean': mean,
    'stdev': stdev
}

used_df = ""
comp_thr = ""
ips = check_output(['hostname', '-I'])
localhost_ip = ips.decode().split(" ")[0]
if os.system("test -f /.dockerenv") == 0:
    localhost_ip = os.environ['HOST_IP']


@bp.route('/', methods=['GET', 'POST'])
def freqvsfreq():
    global comp_thr
    list_of_files = glob.glob(os.path.join(
        current_app.config['UPLOAD_FOLDER']) + "/*")
    latest_file = max(list_of_files, key=os.path.getctime)
    extension = latest_file.rsplit('.', 1)[1].lower()
    match extension:
        case 'pkl':
            df_pickle = open(latest_file, "rb")
            dict_vars['df'] = pickle.load(df_pickle)
        case 'csv':
            dict_vars['df'] = pd.read_csv(latest_file)

    list_var = dict_vars['df'].columns
    if request.method == 'POST':
        if list(request.form.keys()):
            if 'rv_selected' in list(request.form.keys()):
                rvar = request.form['rv_selected']
                if len(dict_vars['df'][rvar].unique()) < 3:
                    return {'response': 'True'}
                return {'response': 'False'}
            dict_vars['root_var'] = request.form['root_var']
            dict_vars['distance'] = request.form['distance']
            dict_vars['predictions'] = request.form['predictions']
            if 'agg_func' in list(request.form.keys()):
                dict_vars['agg_func'] = request.form['agg_func']
            if float(request.form['Slider']) > 0:
                dict_vars['thr'] = float(request.form['Slider'])
            else:
                dict_vars['thr'] = None
            dict_vars['cond_vars'] = request.form.getlist('cond_var')
            dict_vars['a1_param'] = "high"
            if 'auto_thr' in list(request.form.keys()):
                if request.form['auto_thr'] == 'active':
                    if 'a1_param' in list(request.form.keys()):
                        dict_vars['a1_param'] = request.form['a1_param']
                        dict_vars['thr'] = None
            flash('Parameters selected successfully!', 'success')
        return redirect('/bias/freqvsfreq')
    return render_template('freqvsfreq.html', var_list=list_var, local_ip=localhost_ip)


@bp.route('/results', methods=['GET', 'POST'])
def results_fvf():
    bd = FreqVsFreqBiasDetector(distance=dict_vars['distance'], A1=dict_vars['a1_param']
                                )

    results1 = bd.compare_root_variable_groups(
        dataframe=dict_vars['df'],
        target_variable=dict_vars['predictions'],
        root_variable=dict_vars['root_var'],
        threshold=dict_vars['thr']
    )
    results2 = bd.compare_root_variable_conditioned_groups(
        dataframe=dict_vars['df'],
        target_variable=dict_vars['predictions'],
        root_variable=dict_vars['root_var'],
        conditioning_variables=dict_vars['cond_vars'],
        threshold=dict_vars['thr'],
        min_obs_per_group=30
    )
    violations = {k: v for k, v in results2.items() if not v[2]}

    if request.method == "POST":
        csv_data = "condition,num_observations,distance,distance_gt_threshold,threshold,standard_deviation\n"
        for key in list(results2.keys()):
            if len(results2[key]) == 3:
                csv_data += f"{key},{results2[key][0]},{results2[key][1]},{results2[key][2]}\n"
                continue
            csv_data += f"{key},{results2[key][0]},{results2[key][1]},{results2[key][2]},{results2[key][3]},{results2[key][4]}\n"
        # Create a Response with CSV data
        return jsonify({"csv_data": csv_data})

    return render_template('results_freqvsfreq.html', results1=results1, results2=results2, violations=order_violations(violations), local_ip=localhost_ip)


@bp.route('/results/<violation>')
def details_fvf(violation):
    focus_df = dict_vars['df'].query(violation)

    results_viol2 = focus_df.groupby(dict_vars['root_var'])[
        dict_vars['predictions']].value_counts(normalize=True)
    return render_template('violation_specific_fvf.html', viol=violation, res2=results_viol2.to_frame().to_html(classes=['table table-hover mx-auto w-75']))
