import datetime

from markupsafe import escape

from common.currency import currencyConverter, valid_general_locations
from common.data import all_brands, users
from common.util import lookup_belt, lookup_lock


def paginate(listings, pagenum, pagelen, ignore_closed=True):
    if ignore_closed:
        modified_listings = [x for x in listings if x["open"]]
    else:
        modified_listings = [x for x in listings]
    if len(modified_listings) <= pagelen:
        return modified_listings
    start = (pagenum - 1) * pagelen
    end = start + pagelen
    page_listings = modified_listings[start:end]
    return page_listings

def sort_by_views(listings):
    return sorted(listings, key=lambda x: len(x["views"]), reverse=True)

def sort_by_trending(listings):
    return sorted(listings, key=lambda x: len([y for y in x["views"] if datetime.datetime.now() - datetime.datetime.fromisoformat(y) < datetime.timedelta(days=7)]), reverse=True)

def sort_by_newest(listings):
    return list(reversed(listings))

def sort_by_price(listings):
    return sorted(listings, key=lambda x: x["price"])

def filter_belt(listings, belt):
    final = []
    for listing in listings:
        if listing["lpubelts"]:
            if lookup_belt(listing["lpubelts"]) == belt:
                final.append(listing)
    return final

def filter_mechanism(listings, mechanisms):
    final = []
    for listing in listings:
        if listing["lpubelts"]:
            lock = lookup_lock(listing["lpubelts"])
            passed = True
            for mechanism in mechanisms:
                if mechanism not in lock["lockingMechanisms"]:
                    passed = False
            if passed:
                final.append(listing)
    return final

def filter_approx_location(listings, location):
    if location not in valid_general_locations:
        raise ValueError("huh?!?")
    final = []
    for listing in listings:
        user = users[listing["seller"]]
        if user["general_location"] == location:
            final.append(listing)
    return final

def filter_brand(listings, brand):
    if brand not in all_brands:
        raise ValueError("huh?!?")
    final = []
    for listing in listings:
        if listing["lpubelts"]:
            lock = lookup_lock(listing["lpubelts"])
            for makemodel in lock["makeModels"]:
                if makemodel["make"] == brand:
                    final.append(listing)
                    break
    return final

def remove_closed(listings):
    return [x for x in listings if x["open"]]

def localize_price(listing, user_currency="USD"):
    new_listing = listing.copy()
    new_listing["belt"] = lookup_belt(listing["lpubelts"]) if listing["lpubelts"] else "Unranked"
    new_listing["orig_currency"] = listing["currency"]
    new_listing["orig_price"] = listing["price"]
    new_listing["price"] = currencyConverter.convert(listing["price"], listing["currency"], user_currency)
    new_listing["currency"] = user_currency
    return new_listing

def localize_prices(listings, user_currency="USD"):
    new_listings = []
    for listing in listings:
        new_listings.append(localize_price(listing.copy(), user_currency=user_currency))
    return new_listings

def fix_newline(listing):
    new_listing = listing.copy()
    new_listing["desc"] = str(escape(new_listing["desc"]))
    new_listing["desc"] = new_listing["desc"].replace("\n", "<br>")
    return new_listing