from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

bp = Blueprint('admin', __name__, template_folder="../templates/admin", url_prefix="/admin")

@bp.route('/', methods=['GET'])
def admin_home():
    return render_template('admin_home.html')
