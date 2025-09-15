import os
from flask import (
    Flask,
    flash,
    get_flashed_messages,
    redirect,
    request,
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

def get_data_path():
    if app.config['TESTING']:
        return os.path.join(root, 'tests', 'data')
    else:
        return os.path.join(root, 'cms', 'data')

@app.route('/')
def index():
    data = get_data_path()
    files = os.listdir(data) 
    return render_template('index.html', files=files)

@app.route("/<path:file_name>")
def file_content(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)

    if os.path.isfile(file_path):
        if file_name.split('.')[-1] == 'md':
            with open(file_path, 'r') as file:
                content = file.read()
            return render_template('markdown.html', content=markdown(content))
        else:
            return send_from_directory(data, file_name)
    else:
        flash(f'{file_name} does not exist.', 'error')
        return redirect(url_for('index'))

@app.route("/<path:file_name>/download")
def download_file(file_name):
    return send_from_directory(
        get_data_path(), 
        file_name, 
        as_attachment=True
    )

@app.route("/<path:file_name>/edit")
def edit_file(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)

    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        return render_template('edit.html', file_name=file_name, content=content)
    else:
        flash(f'{file_name} does not exist.', 'error')
        return redirect(url_for('index'))

@app.route("/<path:file_name>", methods=["POST"])
def submit_changes(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)
    content = request.form['content']
    with open(file_path, 'w') as file:
        file.write(content)

    flash(f'{file_name} has been edited.', 'success')
    return redirect(url_for('index'))

@app.route("/new")
def new_document():
    return render_template('new.html')

@app.route("/create", methods=["POST"])
def create_document():
    document_name = request.form.get('document_name', '').strip()
    data = get_data_path()
    file_path = os.path.join(data, document_name)

    if len(document_name) == 0:
        flash('A name is required.')
        return render_template('new.html'), 422
    elif os.path.exists(file_path):
        flash(f'{document_name} already exists.')
        return render_template('new.html'), 422
    else:
        with open(file_path, 'w') as file:
            file.write('')
        flash(f'{document_name} was created successfully', 'success')
        return redirect(url_for('index'))

@app.route("/<path:file_name>/delete", methods=["POST"])
def delete_file(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)
    
    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f'{file_name} has been deleted.')
    else:
        flash(f'{file_name} does not exist.')

    return redirect(url_for('index'))

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)