import json, requests
import os

from common.observables import JsonDict, JsonList

def get_filters(locks):
    all_mechanisms = []
    all_brands = []
    for lock in locks:
        try:
            for mechanism in lock["lockingMechanisms"]:
                if mechanism not in all_mechanisms:
                    all_mechanisms.append(mechanism)
        except KeyError:
            pass
        try:
            for makemodel in lock["makeModels"]:
                if makemodel["make"] not in all_brands:
                    all_brands.append(makemodel["make"])
        except KeyError:
            pass
    return all_mechanisms, all_brands

print("Ensuring that files exist...")
os.makedirs("./data", exist_ok=True)
os.makedirs("./user_content", exist_ok=True)
if not os.path.exists("./data/users.json"):
    with open("./data/users.json", "w") as f:
        json.dump({}, f)
if not os.path.exists("./data/listings.json"):
    with open("./data/listings.json", "w") as f:
        json.dump([], f)
if not os.path.exists("./data/wtb.json"):
    with open("./data/wtb.json", "w") as f:
        json.dump([], f)

print("Downloading latest LPUBelts data.json...")
r = requests.get("https://lpubelts.com/data.json")
if r.status_code == 200:
    with open("./data/locks.json", "w") as f:
        json.dump(r.json(), f)
else:
    print("Failed!")

users        = JsonDict('./data/users.json')
locks        = json.load(open('./data/locks.json', 'r'))
listings     = JsonList('./data/listings.json')
wtb_listings = JsonList('./data/wtb.json')
try:
    lpubelts_token = open('./data/lpubelts_token.txt', 'r').read()
except FileNotFoundError:
    lpubelts_token = None

all_mechanisms, all_brands = get_filters(locks)

def reload_all():
    global users, locks, listings, wtb_listings, all_mechanisms, all_brands, lpubelts_token
    users.reload()
    locks = json.load(open('./data/locks.json', 'r'))
    try:
        lpubelts_token = open('./data/lpubelts_token.txt', 'r').read()
    except FileNotFoundError:
        lpubelts_token = None
    listings.reload()
    wtb_listings.reload()
    all_mechanisms, all_brands = get_filters(locks)