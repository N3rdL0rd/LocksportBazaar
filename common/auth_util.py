import bcrypt

from common.data import users
from common.util import generate_random_string, save_users


def authed(token):
    for k, v in users.items():
        if v["token"] == token:
            return {"username": k, **v}

def login_user(username, password):
    if username not in users:
        return False
    if bcrypt.checkpw(password.encode('utf-8'), users[username]["password"].encode('utf-8')):
        return users[username]["token"]
    return False

def logout_user(token):
    for k, v in users.items():
        if v["token"] == token:
            users[k]["token"] = generate_random_string(512)
            save_users()
            return True
    return False
