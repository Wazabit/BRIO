import json
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv

from flask import Flask, render_template, redirect, session, url_for
from flask_cors import CORS

from frontend.views import bias, opacity, risk, admin
from frontend.views.admin_route import client, new_client, project, new_project, charts_admin_home

from frontend.classes.user import User
from frontend.classes.database import Database

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.register_blueprint(bias.bp)
app.register_blueprint(opacity.bp)
app.register_blueprint(risk.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(client.bp)
app.register_blueprint(new_client.bp)
app.register_blueprint(project.bp)
app.register_blueprint(new_project.bp)
app.register_blueprint(charts_admin_home.bp)

app.secret_key = env.get("APP_SECRET_KEY")



oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

app.db = Database()


@app.route('/', methods=['GET'])
#def home():
#    return render_template('homepage.html')
def home():
    if session.get("user") is None:
        btn_login = False
        return render_template(
            "homepage.html",
            btn_login=btn_login
        )
    else:
        data = session.get("user")
        user = User(data.get("userinfo"))
        user.register_update(user, app.db)
        btn_login = True

        if user.role == "Admin":
            return redirect(url_for("admin.admin_home"))
        else:
            return render_template(
                "homepage.html",
                btn_login=btn_login,
                user=user.toJSON(),
                role=user.role,
                session=session.get("user"),
                pretty=json.dumps(session.get("user"), indent=4),
            )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")


@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
