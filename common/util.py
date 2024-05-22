import random
import string
import urllib.parse

from common.data import listings, locks, users

def urlencode(s):
    return urllib.parse.quote(s)

def generate_random_string(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for i in range(length))

def clamp(n, smallest, largest):
    return max(smallest, min(n, largest))

def lookup_belt(id):
    for lock in locks:
        if lock["id"] == id:
            return lock["belt"]
    return None

def lookup_lock(id):
    for lock in locks:
        if lock["id"] == id:
            return lock
    return False

def next_id():
    return listings[-1]["id"] + 1

def save_users():
    print("Warning: save_users is deprecated. Don't worry, common.data now autosaves!")

def queryencode(string):
    return urllib.parse.quote(string)