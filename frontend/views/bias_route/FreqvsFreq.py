import glob
import os
import pickle
from statistics import mean, stdev
from subprocess import check_output
import logging


import pandas as pd
import numpy as np
from flask import (Blueprint, current_app, flash, jsonify,
                   redirect, render_template, request)

from brio.bias.FreqVsFreqBiasDetector import FreqVsFreqBiasDetector
from brio.bias.BiasDetector import BiasDetector
from brio.utils.funcs import order_violations

from brio.risk.HazardFromBiasDetectionCalculator import HazardFromBiasDetectionCalculator
bp = Blueprint('FreqvsFreq', __name__,
               template_folder="../../templates/bias", url_prefix="/freqvsfreq")

dict_vars = {}
agg_funcs = {
    'min': min,
    'max': max,
    'mean': mean,
    'stdev': stdev
}
selected_params = { 
}
display_params = "d-none"
used_df = ""
comp_thr = ""
animation_status = "animated"
ips = check_output(['hostname', '-I'])
localhost_ip = ips.decode().split(" ")[0]
if os.system("test -f /.dockerenv") == 0:
    localhost_ip = os.environ['HOST_IP']


@bp.route('/', methods=['GET', 'POST'])
def freqvsfreq():
    global comp_thr
    global animation_status
    global selected_params
    global display_params
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
            dict_vars['target_type'] = request.form['target_type']
            selected_params['target_type'] = dict_vars['target_type']  
            if 'nbins' in list(request.form.keys()):
                dict_vars['nbins'] = int(request.form['nbins'])
                selected_params['nbins'] = dict_vars['nbins']  
            dict_vars['root_var'] = request.form['root_var']
            selected_params['root_var'] = dict_vars['root_var']
            dict_vars['distance'] = request.form['distance']
            selected_params['distance'] = dict_vars['distance'] 
            dict_vars['predictions'] = request.form['predictions']   
            selected_params['predictions'] = dict_vars['predictions']
            if 'agg_func' in list(request.form.keys()):
                dict_vars['agg_func'] = request.form['agg_func']
                selected_params['agg_func'] = dict_vars['agg_func']  
            if float(request.form['Slider']) > 0:
                dict_vars['thr'] = float(request.form['Slider'])
            else:
                dict_vars['thr'] = None
            dict_vars['cond_vars'] = request.form.getlist('cond_var')      
            selected_params['cond_vars'] = dict_vars['cond_vars']
            dict_vars['a1_param'] = "high"
            if 'auto_thr' in list(request.form.keys()):
                if request.form['auto_thr'] == 'active':
                    if 'a1_param' in list(request.form.keys()):
                        dict_vars['a1_param'] = request.form['a1_param']
                        dict_vars['thr'] = None   
            selected_params['thr'] = dict_vars['thr']  
            selected_params['a1_param'] = dict_vars['a1_param'] 
            display_params = "d-flex"  
            flash('Parameters selected successfully!', 'success')
        animation_status = ""
        return redirect('/bias/freqvsfreq/#selected_params')
    return render_template('freqvsfreq.html', var_list=list_var, local_ip=localhost_ip, animated=animation_status, sel_params=selected_params, d_params=display_params)


@bp.route('/results', methods=['GET', 'POST'])
def results_fvf():

    bd = FreqVsFreqBiasDetector(
        distance=dict_vars['distance'],
        A1=dict_vars['a1_param'],
        target_variable_type=dict_vars['target_type']
    )
    if dict_vars['target_type'] == 'probability':
        results1 = bd.compare_root_variable_groups(
            dataframe=dict_vars['df'],
            target_variable=dict_vars['predictions'],
            root_variable=dict_vars['root_var'],
            threshold=dict_vars['thr'],
            n_bins=dict_vars['nbins']
        )
        results2 = bd.compare_root_variable_conditioned_groups(
            dataframe=dict_vars['df'],
            target_variable=dict_vars['predictions'],
            root_variable=dict_vars['root_var'],
            conditioning_variables=dict_vars['cond_vars'],
            threshold=dict_vars['thr'],
            min_obs_per_group=30,
            n_bins=dict_vars['nbins']
        )
    else:
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

    hc = HazardFromBiasDetectionCalculator()
    results3 = hc.compute_hazard_from_freqvsfreq_or_freqvsref(
        results1,
        results2,
        dict_vars['df'].shape[0],
        dict_vars['cond_vars'],
        weight_logic="group"
    )

    individual_risk = results3.pop(0)
    unconditioned_hazard = results3.pop(0)
    
    conditioned_results_with_hazard = {}
    for k, v in results2.items():
        if v[1] is not None:
            v_list = list(v)
            line_risk = results3.pop(0)
            v_list.insert(1, line_risk)
            conditioned_results_with_hazard[k] = tuple(v_list)

    violations = {k: v for k, v in conditioned_results_with_hazard.items() if not v[3]}

    csv_plot = "condition,num_observations,hazard,distance,standard_deviation\n"
    h_min = 1
    h_max = 0
    d_min = 1
    d_max = 0
    for key in list(violations.keys()):
        csv_plot += f"{key},{violations[key][0]},{violations[key][1]},{violations[key][2]},{violations[key][5]}\n"
        if violations[key][1] < h_min: h_min=violations[key][1]
        if violations[key][1] > h_max: h_max=violations[key][1]
        if violations[key][2] < d_min: d_min=violations[key][2]
        if violations[key][2] > d_max: d_max=violations[key][2]
    logging.warning("data to plot")
    logging.warning(h_min)
    logging.warning(h_max)
    logging.warning(d_min)
    logging.warning(d_max)
    # Create CSV data to plot
    #jsonify({"csv_data": csv_data})

    if request.method == "POST":
        csv_data = "condition,num_observations,distance,distance_gt_threshold,threshold,standard_deviation\n"
        for key in list(results2.keys()):
            if len(results2[key]) == 3:
                csv_data += f"{key},{results2[key][0]},{results2[key][1]},{results2[key][2]}\n"
                continue
            csv_data += f"{key},{results2[key][0]},{results2[key][1]},{results2[key][2]},{results2[key][3]},{results2[key][4]}\n"
        # Create a Response with CSV data
        return jsonify({"csv_data": csv_data})

    return render_template('results_freqvsfreq.html', results1=results1, results2=results2, individual_risk=individual_risk, unconditioned_hazard=unconditioned_hazard, violations=order_violations(violations), local_ip=localhost_ip, sel_params=selected_params, plot_data=csv_plot, h_min=h_min, h_max=h_max, d_min=d_min, d_max=d_max)


@bp.route('/results/<violation>') # USA IN QUALCHE MODO get_frequencies_list_from_probs O I SUO CONTENUTO
def details_fvf(violation):
    focus_df = dict_vars['df'].query(violation)

    if dict_vars['target_type'] == 'probability':
        bd = BiasDetector()
        freqs, _ = bd.get_frequencies_list_from_probs(focus_df, dict_vars['predictions'], 
                                dict_vars['root_var'], sorted(focus_df[dict_vars['root_var']].unique()), dict_vars['nbins'])
        #transform list of frequencies in a Series with multiindex
        predicted_probs_limits = np.round(np.arange(0, 1 + 1/dict_vars['nbins'], 1/dict_vars['nbins']),2)
        predicted_probs_range = [f'{start}-{end}' for start, end in zip(predicted_probs_limits[:-1], predicted_probs_limits[1:])]
        # Create a multi-index
        multi_index = pd.MultiIndex.from_product([sorted(focus_df[dict_vars['root_var']].unique()), predicted_probs_range], names=[dict_vars['root_var'], dict_vars['predictions']])
        results_viol2 = pd.Series(np.concatenate(freqs), index=multi_index, name='freqs')
    else:
        results_viol2 = focus_df.groupby(dict_vars['root_var'])[
            dict_vars['predictions']].value_counts(normalize=True)
    return render_template('violation_specific_fvf.html', viol=violation, res2=results_viol2.to_frame().to_html(classes=['table border-0 table-mirai table-hover w-100 rajdhani-bold text-white m-0']))
