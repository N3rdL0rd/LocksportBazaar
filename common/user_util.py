import datetime
import statistics
import traceback

import bcrypt

from common.data import users
from common.util import generate_random_string, save_users
from common.auth_util import authed

def get_unpushed(token, mark_pushed=True):
    """
    Gets all unpushed notifications for the user corresponding to the passed token.

    :param token: The token of the user to fetch.
    :returns: An array of notifications or None
    """
    res = authed(token)
    if not res:
        return None
    notifs = [notif for notif in res["notifications"] if not notif["pushed"]]
    if mark_pushed:
        mark_notifs_pushed(res["username"])
    return notifs

def mark_notifs_pushed(user):
    for i in range(users[user]["notifications"]):
        users[user]["notifications"][i]["pushed"] = True

def get_user(username):
    for k, v in users.items():
        if k == username:
            return v
    return None

def mark_notifications_read(username):
    for k, v in users.items():
        if k == username:
            for notif in v["notifications"]:
                notif["read"] = True
                notif["pushed"] = True
            save_users()
            return True
    return False

def send_notif(username, text, href=None):
    users[username]["notifications"].append({"time": datetime.datetime.now().isoformat(),
                                             "msg": text,
                                             "href": href,
                                             "read": False,
                                             "pushed": False})
    save_users()

def update_profile(token, discord=None, email=None, name=None, addie=None, currency=None, bio=None, general_location=None):
    for k, v in users.items():
        if v["token"] == token:
            if discord:
                users[k]["discord"] = discord
            if email:
                users[k]["email"] = email
            if name:
                users[k]["name"] = name
            if addie:
                users[k]["addie"] = addie
            if currency:
                users[k]["currency"] = currency
            if bio:
                users[k]["bio"] = bio
            if general_location:
                users[k]["general_location"] = general_location
            save_users()
            return True
    return False

def create_user(username, password):
    if username in users:
        return False
    unique = False
    while not unique:
        token = generate_random_string(512)
        unique = True
        for k, v in users.items():
            if v["token"] == token:
                unique = False
                break
    users[username] = {
        "password": bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "token": token,
        "discord": None,
        "email": None,
        "name": None,
        "addie": None,
        "currency": "USD",
        "approved_seller": False,
        "seller_rating": {},
        "buyer_rating": {},
        "admin": False,
        "created": datetime.datetime.now().isoformat(),
        "bio": "",
        "general_location": None,
        "banned": False,
        "notifications": [{"time": datetime.datetime.now().isoformat(), "msg": "Welcome to LocksportBazaar!", "href": None, "read": False, "pushed": False}],
        "followers": [],
        "following": [],
        "notif_set": "following",
        "wishlist": []
    }
    save_users()
    return True

def change_password(username, password):
    users[username]["password"] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    unique = False
    while not unique:
        token = generate_random_string(512)
        unique = True
        for k, v in users.items():
            if v["token"] == token:
                unique = False
                break
    users[username]["token"] = token

def follow(buyer, seller):
    try:
        if seller in users[buyer]["following"]:
            return True
        users[buyer]["following"].append(seller)
        users[seller]["followers"].append(buyer)
        save_users()
        return True
    except:
        traceback.print_exc()
        return False
    
def unfollow(buyer, seller):
    try:
        if seller not in users[buyer]["following"]:
            return True
        users[buyer]["following"].remove(seller)
        users[seller]["followers"].remove(buyer)
        save_users()
        return True
    except:
        traceback.print_exc()
        return False

def notify_followers(seller, text, href=None):
    for follower in users[seller]["followers"]:
        try:
            send_notif(follower, text, href=href)
        except Exception as e:
            traceback.print_exc()

def is_following(buyer, seller):
    try:
        return seller in users[buyer]["following"]
    except:
        return False

def calc_rating(ratings):
    listratings = []
    for user, rating in ratings.items():
        listratings.append(rating["score"])
    try:
        return statistics.fmean(listratings)
    except statistics.StatisticsError:
        return "no"

def wishlist(username, id):
    if id in users[username]["wishlist"]:
        return False
    users[username]["wishlist"].append(id)
    return True

def unwishlist(username, id):
    if id not in users[username]["wishlist"]:
        return False
    users[username]["wishlist"].remove(id)
    return True

def wished(username, id):
    return id in users[username]["wishlist"]