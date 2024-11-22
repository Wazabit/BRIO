from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

bp = Blueprint('charts_admin_home', __name__, template_folder="../../templates/admin", url_prefix="/admin/charts_admin_home")

@bp.route('/', methods=['GET'])
def charts_admin_home():
    return render_template('charts_admin_home.html')
