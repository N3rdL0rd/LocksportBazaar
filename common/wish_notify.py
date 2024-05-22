from common.data import users, listings, locks
from common.user_util import send_notif

def check_wishlists(listing):
    for user in users:
        check_wishlist(user, listing)

def check_wishlist(user, listing):
    if listing["id"] in user["wishlist"]:
        send_notif(user, f"Your wishlisted listing <i>{listing['title']}</i> has been updated!", f"/listing/{listing['id']}")
        return True
    if listing["lpubelts"] in user["wishlist"]:
        send_notif(user, f"A listing for your wishlisted lock <i>{listing['title']}</i> has been updated!", f"/listing/{listing['id']}")
        return True
    return False

def get_all_listings(lpubelts_id):
    res = []
    for listing in listings:
        if listing["lpubelts"] == lpubelts_id:
            res.append(listing)
    return res

def get_wishlist_listings(user):
    res_normal = []
    res_lpubelts = []
    # get all listings by exact ids (type int) and then get lpubelts ones and tack them on the end with their names (type str)
    for item in user["wishlist"]:
        for listing in listings:
            if listing["id"] == item:
                res_normal.append(listing)
                break
    for item in user["wishlist"]:
        if isinstance(item, str):
            for lock in locks:
                if lock["id"] == item:
                    res_lpubelts.append([lock, get_all_listings(lock["id"])])
                    break
    return res_normal, res_lpubelts
            