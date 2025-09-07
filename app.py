import os
from flask import (
    Flask,
    render_template,
    send_from_directory,
)
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'

root = os.path.abspath(os.path.dirname(__file__))
data = os.path.join(root, 'cms', 'data')
app.config['UPLOAD_FOLDER'] = data

@app.route('/')
def index():
    documents = os.listdir(data) 
    return render_template('index.html', documents=documents)

@app.route("/files/<path:name>")
def file_content(name):
    return send_from_directory(data, name)

@app.route("/download/<path:name>")
def download_file(name):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], name, as_attachment=True
    )

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)