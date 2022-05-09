from functools import wraps
from flask import redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(pwd):
    # return bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
    return generate_password_hash(pwd)

def check_password(pwd, hashed_pwd):
    # return bcrypt.checkpw(pwd.encode('utf-8'), hashed_pwd.encode())
    return check_password_hash(hashed_pwd,pwd)


def check_message():
    msg = {}
    msg['there'] = 0
    if session.get("message") is not None:
        print("message there!")
        message = session['message']
        if message['there'] == 1:
            print("yes there")
            if "title" in message:
                msg['title'] = message['title']
                message.pop('title')
            if "mode" in message:
                msg['mode'] = message['mode']
                message.pop('mode')
            msg['there'] = 1
            message['there'] = 0
        session['message'] = message
        print(session['message'])
    print(msg)
    return msg

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # #print('decorated')
        # #print(session)
        if 'login' in session:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('show_login'))

    return decorated