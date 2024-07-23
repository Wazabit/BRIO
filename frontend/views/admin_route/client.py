from flask import Flask, render_template, request, redirect, flash, url_for, session, Response, jsonify, Blueprint, current_app

bp = Blueprint('client', __name__, template_folder="../../templates/admin", url_prefix="/admin/client")

@bp.route('/', methods=['GET'])
def client():
    return render_template('client.html')
