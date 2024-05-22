import datetime
import json

users = json.load(open('users.json'))
listings = json.load(open('listings.json'))

def import_seller(seller):
    if seller["name"] not in users:
        users[seller["name"]] = {
            "password": "$2b$12$VTDre1NeznaDjCI37HFdveKfMmCAf7tNqRlfMqF2LY24bjxJ5vYVm",
            "token": "CHANGEME",
            "discord": None,
            "email": None,
            "name": None,
            "addie": None,
            "currency": "USD",
            "approved_seller": True,
            "buyer_rating": {},
            "seller_rating": {},
            "admin": False,
            "created": datetime.datetime.now().isoformat(),
            "notifications": [],
            "bio": "",
            "general_location": None,
            "banned": False,
            "followers": [],
            "following": [],
            "notif_set": "following",
            "wishlist": []
        }
    for listing in seller["listings"]:
        listing["id"] = len(listings) + 1
        listing["seller"] = seller["name"]
        i = 0
        for image in listing["imgs"]:
            if "imgur.com" in image:
                listing["imgs"][i] = image.replace(".jpg", ".jpeg").replace("https://i.imgur.com/", "/imgur/")
            i += 1
        listings.append(listing)
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

    with open('listings.json', 'w') as f:
        json.dump(listings, f, indent=4)

def import_sellers(sellers):
    for seller in sellers:
        import_seller(seller)

if __name__ == "__main__":
    import_sellers(json.load(open("converted_listings.json")))