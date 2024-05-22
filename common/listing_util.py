import datetime
import json

from common.data import listings, users
from common.util import lookup_belt, next_id
from common.wish_notify import check_wishlists

def get_listing(id):
    for listing in listings:
        if listing["id"] == id:
            return listing
    return None

def add_listing(token, title, price, desc, imgs, quantity, currency="USD", condition="Unknown/Other", lpubelts=False):
    for k, v in users.items():
        if v["token"] == token and v["approved_seller"]:
            if lpubelts:
                belt = lookup_belt(lpubelts)
            else:
                belt = None
            listing = {
                "title": title,
                "price": price,
                "desc": desc,
                "imgs": imgs,
                "quantity": quantity,
                "seller": k,
                "open": True,
                "id": next_id(),
                "currency": currency,
                "lpubelts": lpubelts,
                "belt": belt,
                "condition": condition,
                "date": datetime.datetime.now().isoformat(),
                "views": []
            }
            listings.append(listing)
            check_wishlists(listing)
            return True
    return False

def close_listing(token, id):
    for k, v in users.items():
        if v["token"] == token:
            for i in range(len(listings)):
                if listings[i]["id"] == id and listings[i]["seller"] == k:
                    listings[i]["open"] = False
                    return True
    return False

def _close_listing(id):
    for i in range(len(listings)):
        if listings[i]["id"] == id:
            listings[i]["open"] = False
            return True
    return False

def open_listing(token, id):
    for k, v in users.items():
        if v["token"] == token:
            for i in range(len(listings)):
                if listings[i]["id"] == id and listings[i]["seller"] == k:
                    listings[i]["open"] = True
                    check_wishlists(listings[i])
                    return True
    return False

def _open_listing(id):
    for i in range(len(listings)):
        if listings[i]["id"] == id:
            listings[i]["open"] = True
            return True
    return False

def modify_listing(token, id, title, price, desc, quantity, currency, lpubelts, condition):
    for k, v in users.items():
        if v["token"] == token:
            for i in range(len(listings)):
                if listings[i]["id"] == id and listings[i]["seller"] == k:
                    listings[i]["title"] = title
                    listings[i]["price"] = price
                    listings[i]["desc"] = desc
                    listings[i]["quantity"] = quantity
                    listings[i]["currency"] = currency
                    listings[i]["lpubelts"] = lpubelts
                    listings[i]["condition"] = condition
                    check_wishlists(listings[i])
                    return True
    return False

def get_listings(username):
    res = []
    for listing in listings:
        if listing["seller"] == username:
            res.append(listing)
    return res

def log_listing_view(id):
    for listing in listings:
        if listing["id"] == id:
            listing["views"].append(datetime.datetime.now().isoformat())
            return True
    return False

def change_imgs(id, imgs):
    for i in range(len(listings)):
        if listings[i]["id"] == id:
            listings[i]["imgs"] = imgs
            return True
    return False