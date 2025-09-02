import os
from flask import Flask
from werkzeug.exceptions import NotFound

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'

@app.route('/')
def index():
    return 'Getting Started'

if __name__ == "__main__":
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(debug=False)
    else:
        app.run(debug=True, port=5003)