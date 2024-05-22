import datetime
import json
import locale
import random
import re
import string
import traceback

import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials
from rapidfuzz import fuzz

from common.currency import currency_symbols

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def generate_random_string(length):
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choice(alphabet) for i in range(length))

proceed = True
try:
    credentials = ServiceAccountCredentials.from_json_keyfile_name('./data/token.json', ['https://spreadsheets.google.com/feeds'])
except:
    print("No service account found. Google-based features will not work.")
    proceed = False

sheets_data = {
    '12con-dVmTtK1WltONMbtaNJ77EFfm8W9EJ6m0Qca2nc': {
        'owner': 'Red Wanderer',
        'style': 'makemodel',
        'infer_id': True,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 4,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8
        },
        'desc_mapping': {
            'format': 3,
            'picked_as': 5,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}, Picked as {picked_as}. Additional notes: {notes}',
        'exclude_header': 1,
        'weird_comma': False
    },
    '1_Dk619Y3Zj_zsLHKLxGZlRdgSUH1pF0u2BxFScgJPXc': {
        'owner': 'amvgaert',
        'style': 'makemodel',
        'infer_id': False,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 5,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8,
            'lpubelts': 11
        },
        'desc_mapping': {
            'format': 4,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}. Additional notes: {notes}',
        'exclude_header': 5,
    'weird_comma': False
    },
    '1mE2dBFLCvaiY2jKZZafI5xCfR1VvJbysiJjwcR0l6jw': {
        'owner': 'Clefmentine',
        'style': 'makemodel',
        'infer_id': False,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 5,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8,
            'lpubelts': 11
        },
        'desc_mapping': {
            'format': 4,
            'picked_as': 3,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}, Picked as {picked_as}. Additional notes: {notes}',
        'exclude_header': 1,
    'weird_comma': False
    },
    "1eT3kh6vzOEXKWIeHdgmbIIkSQ0wrcAZJODOVhN-0NTE": {
        'owner': 'Florida Man Picks',
        'style': 'makemodel',
        'infer_id': False,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 5,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8,
            'lpubelts': 11
        },
        'desc_mapping': {
            'format': 4,
            'picked_as': 3,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}, Picked as {picked_as}. Additional notes: {notes}',
        'exclude_header': 3,
    'weird_comma': False
    },
    "11hnlj17dcg56Hrpx41zlMxBB2UKbUAAXU0xEAfqiKzM": {
        'owner': 'NiXXeD',
        'style': 'makemodel',
        'infer_id': False,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 5,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8,
            'lpubelts': 11
        },
        'desc_mapping': {
            'format': 4,
            'picked_as': 3,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}, Picked as {picked_as}. Additional notes: {notes}',
        'exclude_header': 3,
    'weird_comma': False
    },
    "1R9GtWZoOx_XjpPZWmSmYd31ukPOsU-9s_Et_P5xK2gw": {
        'owner': 'Rxpert',
        'style': 'makemodel',
        'infer_id': False,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 5,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8,
            'lpubelts': 11
        },
        'desc_mapping': {
            'format': 4,
            'picked_as': 3,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}, Picked as {picked_as}. Additional notes: {notes}',
        'exclude_header': 4,
    'weird_comma': False
    },
    "1TK8ghd7dgZ8q1n_HNXx7c152qlry44I6RNmuwMH7cxk": {
        'owner': 'LockSkipper',
        'style': 'makemodel',
        'infer_id': False,
        'mapping': {
            'make': 0,
            'model': 1,
            'belt': 2,
            'condition': 5,
            'keys': 6,
            'quantity': 7,
            'image': 9,
            'price': 8,
            'lpubelts': 11
        },
        'desc_mapping': {
            'format': 4,
            'notes': 10
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}. Additional notes: {notes}',
        'exclude_header': 4,
    'weird_comma': False
    },
    "1YjvFqYpRIPRE_z_U-cjRWq-C382kGw0PawTr7xKklwo": {
        'owner': 'escapegoat',
        'style': 'unified',
        'infer_id': True,
        'mapping': {
            'quantity': 0,
            'title': 1,
            'belt': 5,
            'keys': 7,
            'image': 7,
            'price': 6,
        },
        'desc_mapping': {
            'format': 2,
            'pickedas': 3,
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}, Picked as: {pickedas}',
        'exclude_header': 6,
    'weird_comma': False
    },
    "1UFcTNlNqmdzXnGbzMgcO5qsqvBLQbh-WGHd8EZESU8E": {
        'owner': 'Phalangical',
        'style': 'unified',
        'infer_id': True,
        'mapping': {
            'quantity': 7,
            'title': 0,
            'belt': 1,
            'keys': 2,
            'image': 6,
            'price': 3,
        },
        'desc_mapping': {
            'notes': 4
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Notes: {notes}',
        'exclude_header': 1,
    'weird_comma': False
    },
    "1MrD08QwWAs_3_HJwV3kJQK9YLbbkFif5Wb0MEL6f9fc": {
        'owner': 'Wyte',
        'style': 'unified',
        'infer_id': True,
        'mapping': {
            'quantity': 5,
            'title': 0,
            'belt': 1,
            'keys': 4,
            'image': 6,
            'price': 3,
        },
        'desc_mapping': {
            'notes': 6,
            'format': 2
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Format: {format}. Notes: {notes}',
        'exclude_header': 2,
    'weird_comma': False
    },
    "1B3nw8NlXZuGu6fRZuOSUjLo6TxM8yfwSjbn_YL7g0GQ": {
        'owner': 'JayDee',
        'style': 'unified',
        'infer_id': True,
        'mapping': {
            'quantity': 3,
            'title': 0,
            'belt': 6,
            'keys': 3,
            'image': 7,
            'price': 4
        },
        'desc_mapping': {
            'notes': 8
        },
        'unlisted_style': 'quantity',
        'desc_format': 'Remarks: {notes}',
        'exclude_header': 21,
        'weird_comma': True,
        'default_currency': 'EUR'
    },
}

if proceed:
    client = gspread.authorize(credentials)
    symbols_currency = dict((v,k) for k,v in currency_symbols.items())
    locks = json.load(open("./data/locks.json"))

def parse_price(price_str, has_weird_comma, default_currency=None):
    if not has_weird_comma:
        for symbol, currency in symbols_currency.items():
            if price_str.strip().startswith(symbol):
                return float(price_str.strip().replace(",", "").split(symbol)[1]), currency
        return float(price_str.strip().replace(",", "")), "USD" if not default_currency else default_currency
    else:
        for symbol, currency in symbols_currency.items():
            if price_str.strip().startswith(symbol):
                return float(price_str.strip().replace(",", ".").split(symbol)[1]), currency
        return float(price_str.strip().replace(",", ".")), "EUR" if not default_currency else default_currency

def format_desc(format_str, mapping, row):
    desc = format_str
    for key, index in mapping.items():
        if not row[index] or not row[index].strip():
            val = "None"
        else:
            val = row[index].strip()
        desc = desc.replace('{' + key + '}', val)
    return desc

def find_lpubelts(name, belt):
    ratios = []
    for lock in locks:
        for makeModel in lock['makeModels']:
            try:
                ratios.append([fuzz.WRatio(makeModel["make"] + " " + makeModel["model"], name), lock["id"], lock["belt"], makeModel["make"] + " " + makeModel["model"]])
            except:
                continue
    if not belt or not belt.strip() or belt.strip().lower() in ["none", "n/a", "unranked", "unknown", "not checking"]:
        return sorted(ratios, key=lambda x: x[0], reverse=True)[0][1]
    else:
        if name == "assa twin pro":
            print("\n\n\n\n")
        belt_aliases = {
            r"(bb)(\d)": r"black \2",
            r"(black)(\d)": r"black \2",
        }
        new_belt = belt
        for alias, corrected in belt_aliases.items():
            new_belt = re.sub(alias, corrected, new_belt)

        new_ratios = [ratio for ratio in ratios if ratio[2].lower() == new_belt.lower()]
        try:
            return sorted(new_ratios, key=lambda x: x[0], reverse=True)[0][1]
        except:
            return None

def lookup_belt(id):
    for lock in locks:
        if lock["id"] == id:
            return lock["belt"]
    return None

def fix_quantity(quantity_str):
    final = ''.join([c for c in quantity_str if c in '1234567890.'])
    try:
        int(final)
    except ValueError:
        return 0
    return final

def match_condition(condition):
    condition_maps = {
        "nos": "New",
        "new in box": "New",
        "refurbished": "Used",
        "good": "New",
        "like new": "Used",
        "new w/ card": "New",
    }
    valid_conditions = [
        "unknown/other",
        "new",
        "used",
        "open box"
    ]
    if condition.lower() in valid_conditions:
        return condition.title()
    if condition.lower() not in condition_maps.keys():
        return "Unknown/Other"
    else:
        return condition_maps[condition.lower()]

def find_imgs(image_link, lpubelts, force_lpubelts=False):
    if "imgur.com" in image_link and not force_lpubelts:
        try:
            headers = {'Authorization': open('./data/imgur_client_id.txt').read().strip()}
            image_link = image_link.replace("imgur.com/gallery/", "imgur.com/a/")
            if 'imgur.com/a/' not in image_link or not 'imgur.com/gallery/' not in image_link:
                response = requests.get('https://api.imgur.com/3/image/' + image_link.split('/')[-1], headers=headers)
                data = response.json()
                try:
                    return [data['data']['link']], None
                except KeyError:
                    return find_imgs(image_link, lpubelts, force_lpubelts=True)
            else:
                album_id = image_link.split('/')[-1]
                response = requests.get('https://api.imgur.com/3/album/' + album_id, headers=headers)
                data = response.json()
                if data['success']:
                    return [img['link'] for img in data['data']['images']], None
                else:
                    raise ValueError("Unable to get images from imgur gallery.")
        except requests.exceptions.SSLError:
            return find_imgs(image_link, lpubelts, force_lpubelts=True)
    elif "drive.google.com" in image_link and not force_lpubelts:
        drive_id = image_link.split("https://drive.google.com/file/d/")[1].split("/view")[0]
        return [f"https://drive.google.com/thumbnail?id={drive_id}&sz=w1000"], None # TODO: just download the damn image
    else:
        print("Oh well. Using placeholder...")
        return ["/static/photoSoonL-16x9-dark.png"], "\nNo images were found, so a placeholder was used."
    
def get_data(sheet_id, meta):
    sheet = client.open_by_key(sheet_id).sheet1
    all_values = sheet.get_all_values()
    
    # split data
    if meta["unlisted_style"] == "delimiter":
        i = 0
        found = False
        for row in all_values:
            j = 0
            for col in row:
                if col == meta["unlisted_delimiter"]:
                    found = True
                    break
                j += 1
            if found:
                break
            i += 1
        all_values = all_values[meta["exclude_header"]:i]
    else:
        all_values = [row for row in all_values[meta["exclude_header"]:] if row[meta['mapping']['quantity']] and row[meta['mapping']['quantity']].strip() != '' and int(fix_quantity(row[meta['mapping']['quantity']])) > 0]    

    errors = []
    listings = []
    for row in all_values:
        title = None
        if meta["style"] == "makemodel":
            title = row[meta['mapping']['make']] + " " + row[meta['mapping']['model']]
        else:
            title = row[meta['mapping']['title']]
        if not title or not title.strip():
            errors.append([row, "Unable to find title"])
            continue
        try:
            try:
                price, currency = parse_price(row[meta['mapping']['price']], meta['weird_comma'], default_currency=meta['default_currency'])
            except:
                price, currency = parse_price(row[meta['mapping']['price']], meta['weird_comma'])
        except Exception as e:
            traceback.print_exc(e)
            errors.append([row, "Unable to parse price"])
            continue
        desc = format_desc(meta['desc_format'], meta['desc_mapping'], row)
        if meta['infer_id']:
            lpubelts = find_lpubelts(title, row[meta['mapping']['belt']])
        else:
            try:
                lpubelts = row[meta['mapping']['lpubelts']].split("https://share.lpubelts.com/?id=")[1].split("&name=")[0]
            except:
                lpubelts = None
        belt = lookup_belt(lpubelts) if lpubelts else None
        quantity = int(fix_quantity(row[meta['mapping']['quantity']]))
        try:
            condition = match_condition(row[meta['mapping']['condition']])
        except KeyError:
            condition = "Unknown/Other"
        try:
            imgs, desc_append = find_imgs(row[meta['mapping']['image']], lpubelts)
        except ValueError:
            errors.append([row, "Unable to automatically fetch images"])
            continue
        try:
            keys = row['meta']['mapping']['keys']
        except:
            keys = "Unknown"
        if desc_append:
            desc += desc_append
        if len(imgs) == 0:
            errors.append([row, "Unable to automatically fetch images"])
            continue
        print(imgs)
        print(f"{title} ({belt}), {condition}: {str(price)} {currency}\n{desc}")
        listings.append({
            "title": title,
            "price": price,
            "desc": desc,
            "imgs": imgs,
            "quantity": quantity,
            "seller": None,
            "open": True,
            "id": None,
            "keys": keys,
            "currency": currency,
            "lpubelts": lpubelts,
            "belt": belt,
            "condition": condition,
            "date": datetime.datetime.now().isoformat(),
            "views": []
        })
    return listings, errors

def get_data_multi(sellers):
    final_data = []
    for sheet_id, meta in sellers.items():
        listings, errors = get_data(sheet_id, meta)
        final_data.append({
            "name": meta["owner"],
            "listings": listings,
            "errors": errors
        })
    return final_data

if __name__ == "__main__" and proceed:
    json.dump(get_data_multi(sheets_data), open("converted_listings.json", "w"), indent=4)