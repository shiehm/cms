from bcrypt import checkpw, gensalt, hashpw
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
from functools import wraps
from markdown import markdown
import os
import shutil
from werkzeug.exceptions import NotFound
import yaml

app = Flask(__name__)
app.secret_key = 'secret1'
root = os.path.abspath(os.path.dirname(__file__))

def get_data_path():
    if app.config['TESTING']:
        return os.path.join(root, 'tests', 'data')
    else:
        return os.path.join(root, 'cms', 'data')

def get_users_path():
    if app.config['TESTING']:
        return os.path.join(root, 'tests')
    else:
        return os.path.join(root, 'cms')

def load_users_credentials():
    users_path = get_users_path()
    users_file = os.path.join(users_path, 'users.yaml')
    with open(users_file, 'r') as file:
        return yaml.safe_load(file)

def validate_user(username, password):
    users = load_users_credentials()
    if username in users:
        stored_password = users[username].encode('utf-8')
        return checkpw(password.encode('utf-8'), stored_password)
    else:
        return False

def logged_in():
    return 'username' in session

def require_login(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if not logged_in():
            flash('You must be signed in to do that.')
            return redirect(url_for('show_signin_form'))
        return func(*args, **kwargs)
    return decorated_func

def validate_file_type(file):
    accepted_types = ['txt', 'md']
    return file.split('.')[-1] in accepted_types

@app.route('/users/signin')
def show_signin_form():
    return render_template('signin.html')

@app.route('/users/signup')
def show_signup_form():
    return render_template('signup.html')

@app.route('/users/signup', methods=["POST"])
def signup():
    username = request.form.get('username')
    password = request.form.get('password')
    users = load_users_credentials()

    if len(username) == 0 or len(password) == 0:
        flash('Username and Password are required.')
        return render_template('signup.html'), 422
    if username in users:
        flash('Username has been taken')
        return render_template('signup.html'), 422
    else:
        users_path = get_users_path()
        users_file = os.path.join(users_path, 'users.yaml')
        
        hashed = hashpw(password.encode('utf-8'), gensalt())
        users[username] = hashed.decode('utf-8')

        with open(users_file, 'w') as file:
            yaml.dump(users, file)
        
        flash('User created.', 'success')
        return redirect(url_for('show_signin_form'))

@app.route('/users/signin', methods=["POST"])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if validate_user(username, password):
        session['logged_in'] = True
        session['username'] = username
        flash('Welcome')
        return redirect(url_for('index'))
    else:
        flash('Invalid credentials')
        return render_template('signin.html'), 422

@app.route('/users/signout', methods=["POST"])
def signout():
    session['logged_in'] = False
    session.pop('username')
    flash('You have been signed out')
    return redirect(url_for('index'))

@app.route('/')
def index():
    data = get_data_path()
    files = os.listdir(data)

    image_path = os.path.join(root, 'static', 'img')
    images = os.listdir(image_path)

    max_length = max([len(file) for file in files]+[0])
    return render_template('index.html', 
                            files=files, 
                            images=images,
                            max_length=max_length
                            )

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
@require_login
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
@require_login
def submit_changes(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)
    content = request.form['content']
    with open(file_path, 'w') as file:
        file.write(content)

    flash(f'{file_name} has been updated.', 'success')
    return redirect(url_for('index'))

@app.route("/new")
@require_login
def new_document():
    return render_template('new.html')

@app.route("/create", methods=["POST"])
@require_login
def create_document():
    document_name = request.form.get('document_name', '').strip()
    data = get_data_path()
    file_path = os.path.join(data, document_name)

    if len(document_name) == 0:
        flash('A name is required.')
        return render_template('new.html'), 422
    elif not validate_file_type(document_name):
        flash('Invalid file type.')
        return render_template('new.html'), 422
    elif os.path.exists(file_path):
        flash(f'{document_name} already exists.')
        return render_template('new.html'), 422
    else:
        with open(file_path, 'w') as file:
            file.write('')
        flash(f'{document_name} has been created', 'success')
        return redirect(url_for('index'))

@app.route("/<path:file_name>/delete", methods=["POST"])
@require_login
def delete_file(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)
    
    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f'{file_name} has been deleted.')
    else:
        flash(f'{file_name} does not exist.')

    return redirect(url_for('index'))

@app.route("/<path:file_name>/duplicate_file", methods=["POST"])
@require_login
def duplicate_file(file_name):
    data = get_data_path()
    file_path = os.path.join(data, file_name)
    copy_path = file_path + '(copy)'
    shutil.copyfile(file_path, copy_path)
    return redirect(url_for('index'))

@app.route("/upload")
@require_login
def upload():
    return render_template('upload.html')

@app.route("/upload_image", methods=["POST"])
@require_login
def upload_image():
    image = request.files.get('image_name')
    if image and image.filename != '':
        image.save(os.path.join('static', 'img', image.filename))
    return redirect(url_for('index'))

@app.route("/<path:image_name>/show_image")
@require_login
def show_image(image_name):
    image_path = os.path.join('static', 'img', image_name)
    return render_template('show_image.html', 
                            image_name=image_name, 
                            image_path=image_path
                            )

@app.route("/<path:image_name>/delete_image", methods=["POST"])
@require_login
def delete_image(image_name):
    image_path = os.path.join('static', 'img', image_name)
    
    if os.path.isfile(image_path):
        os.remove(image_path)
        flash(f'{image_name} has been deleted.')
    else:
        flash(f'{image_name} does not exist.')

    return redirect(url_for('index'))

@app.route("/<path:image_name>/download_image")
@require_login
def download_image(image_name):    
    return send_from_directory(
        os.path.join('static', 'img'),
        image_name,
        as_attachment=True
    )

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)