import base64
from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask_login import LoginManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

mysql = MySQL(app)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

from auth.routes import auth_bp
app.register_blueprint(auth_bp)

@app.route("/")
def welcome():
    return render_template('welcome.html')

@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')


if __name__ == '__main__':
    app.run(debug=True)
