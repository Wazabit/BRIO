from flask import request
import pandas as pd
import numpy as np
import os


def allowed_file(filename: str) -> str:
    ALLOWED_EXTENSIONS = {'pkl', 'csv', 'ipynb', 'py'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_file_logo(filename: str) -> str:
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    return filename.rsplit('.', 1)[1].lower()


def handle_multiupload(req: request, label: str, path: str) -> None:
    files_list = req.files.getlist(label)
    for file in files_list:
        name = file.filename
        save_path = os.path.join(path, name)
        file.save(save_path)


def handle_ref_distributions(rootvar: str, targetvar: str, df: pd.DataFrame, dict_vars: dict) -> list:
    nroot = len(df[rootvar].unique())
    if dict_vars['target_type'] == 'probability':
        ntarget = dict_vars['nbins']
    else:
        ntarget = len(df[targetvar].unique())
    final_list = []
    intermediate_list = []
    for i in range(nroot):
        for j in range(ntarget):
            intermediate_list.append(dict_vars[f'prob_{i}_{j}'])
        final_list.append(np.array(intermediate_list))
        intermediate_list = []
    return final_list


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower().str.replace('-', '_')
    return df


def order_violations(viol: dict) -> dict:
    # Function to get the middle value from the tuple
    def get_middle_value(item):
        middle_value = item[1]
        if type(middle_value) == list:
            return max(middle_value)
        return middle_value

    # Sort entries with valid middle values
    sorted_entries_with_middle_values = sorted(
        ((key, value) for key, value in viol.items() if get_middle_value(value) is not None),
        key=lambda x: get_middle_value(x[1]), reverse=True)

    # Sort entries with None middle values and append them at the end
    sorted_dict = dict(sorted_entries_with_middle_values + [(key, value)
                                                            for key, value in viol.items() if
                                                            get_middle_value(value) is None])
    return sorted_dict


def write_reference_distributions_html(rootvar: str, targetvar: str, df: pd.DataFrame, target_type: str,
                                       n_bins: int) -> str:
    nroot = len(df[rootvar].unique())
    if target_type == 'probability':
        ntarget = n_bins
    else:
        ntarget = len(df[targetvar].unique())
    tot_refs = nroot * ntarget
    tot_html = ""
    nrows = tot_refs // 4
    if nrows % 4 != 0:
        nrows += 1
    c = 0
    d = 0
    current_value = 1
    current_target = ntarget
    for n in range(nrows):
        tot_html += f'<div class="row" id="ref_dist{n}">'
        for j in range(tot_refs):
            if j != 0 and j % 4 == 0:
                break
            tot_refs -= 1

            if current_target == 0:
                current_value = 1
                current_target = ntarget

            value = round((current_value / current_target), 2)
            tot_html += '<div class="col-3 d-flex flex-column align-items-center">'
            tot_html += f'<label for="prob_{c}_{d}">{rootvar}_{c}_{targetvar}_{d}_ref</label>'
            tot_html += f'<input onchange="updateRefValue({c},{d})" type="number" data-tot={ntarget} class="form-control number-mirai w-100 mb-3 ref-input" value={value} name="prob_{c}_{d}" id="prob_{c}_{d}" min="0" max="1" step=".01">'
            d += 1
            if d == ntarget:
                d = 0
                c += 1

            current_value = current_value - value
            current_target -= 1

            tot_html += '</div>'

        tot_html += '</div>'
    return tot_html


def upload_folder(folder: str, user_id: str) -> str:
    user_folder = folder + "/" + user_id
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
    return user_folder
