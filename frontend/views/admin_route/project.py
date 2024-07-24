from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

bp = Blueprint('project', __name__, template_folder="../../templates/admin", url_prefix="/admin/client/project")

@bp.route('/', methods=['GET'])
def project():
    return render_template('project.html')
