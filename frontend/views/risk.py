from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

bp = Blueprint('risk', __name__, template_folder="../templates/bias", url_prefix="/risk")

@bp.route('/', methods=['GET'])
def risk_home():
    return render_template('underconstruction.html')
