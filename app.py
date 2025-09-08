import os
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    render_template,
    send_from_directory,
    session,
    url_for,
)
from markdown import markdown
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.secret_key = 'secret1'

root = os.path.abspath(os.path.dirname(__file__))
data = os.path.join(root, 'cms', 'data')
app.config['UPLOAD_FOLDER'] = data

@app.route('/')
def index():
    files = os.listdir(data) 
    return render_template('index.html', files=files)

@app.route("/files/<path:file_name>")
def file_content(file_name):
    file_path = os.path.join(data, file_name)

    if file_name in os.listdir(data):
        if file_name.split('.')[-1] == 'md':
            with open(file_path, 'r') as file:
                content = file.read()
            return markdown(content)
        else:
            return send_from_directory(data, file_name)
    else:
        flash(f'{file_name} does not exist.', 'error')
        return redirect(url_for('index'))

@app.route("/download/<path:file_name>")
def download_file(file_name):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], file_name, as_attachment=True
    )

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)