from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

bp = Blueprint('new_project', __name__, template_folder="../../templates/admin", url_prefix="/admin/new_project")

@bp.route('/', methods=['GET', 'POST'])
def new_project():
    return render_template('new_project.html')
