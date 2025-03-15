import hashlib
import json
import functools
from flask import session, redirect, url_for

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def load_users():
    try:
        with open("D:/Tools/PC Controller/users.json", 'r') as f:
            return json.load(f)['users']
    except:
        return []

def hash_password(password):
    encoded = password.encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()
