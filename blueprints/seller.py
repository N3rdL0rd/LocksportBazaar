import json
import os
import threading

from flask import Blueprint, redirect, request
from werkzeug.utils import secure_filename

from common.auth_util import authed
from common.browse_util import localize_prices
from common.constants import UPLOAD_FOLDER
from common.currency import currencies, currency_symbols
from common.data import listings, users
from common.listing_util import (add_listing, change_imgs, close_listing,
                                 get_listings, modify_listing, open_listing,
                                 get_listing)
from common.render import render_template
from common.sheet_util import imports, sheet_import
from common.user_util import calc_rating, get_user, notify_followers, is_following, send_notif
from common.util import generate_random_string, next_id, urlencode

seller_blueprint = Blueprint('seller_blueprint', __name__,
                        template_folder='templates')

@seller_blueprint.route('/seller/open/<id>')
def seller_open(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile"))
    if open_listing(res["token"], int(id)):
        return redirect("/profile#listings")
    else:
        return render_template('error.html', error="Not authed", status_code="401")
    return render_template('error.html', error="Listing not found", status_code="404")

@seller_blueprint.route('/seller/close/<id>')
def seller_close(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile"))
    if close_listing(res["token"], int(id)):
        return redirect("/profile#listings")
    else:
        return render_template('error.html', error="Not authed", status_code="401")
    return render_template('error.html', error="Listing not found", status_code="404")

@seller_blueprint.route('/seller/delete/<id>')
def seller_delete(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile"))
    for k, v in users.items():
        if v["token"] == res["token"]:
            for i in range(len(listings)):
                if listings[i]["id"] == int(id) and listings[i]["seller"] == k:
                    del listings[i]
                    return redirect("/profile#listings")
    return render_template('error.html', error="Not authed", status_code="401")

@seller_blueprint.route('/seller/modify/<id>', methods=['GET', 'POST'])
def seller_modify(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile"))
    if request.method == 'GET':
        return render_template('modify.html', listing=get_listing(int(id)), currencies=currencies)
    else:
        required_fields = ["title", "desc", "price", "currency", "quantity", "lpubelts", "imgs", "condition"]
        for field in required_fields:
            if field not in request.form:
                return render_template('modify.html', error="Missing required field", listing=get_listing(int(id)), currencies=currencies)
        modify_listing(res["token"], int(id), request.form['title'], float(request.form['price']), request.form['desc'], int(request.form['quantity']), request.form['currency'], request.form['lpubelts'], request.form['condition'])
        change_imgs(int(id), json.loads(request.form['imgs'].replace("'", '"')))
        return redirect("/profile#listings")

@seller_blueprint.route("/seller/new", methods=['GET', 'POST'])
def seller_new():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile"))
    if request.method == 'GET':
        return render_template('new.html', currencies=currencies, user_currency=res["currency"])
    else:
        required_fields = ["title", "desc", "price", "currency", "quantity", "lpubelts", "condition"]
        for field in required_fields:
            if field not in request.form:
                return render_template('new.html', error="Missing required field", currencies=currencies)
        if not request.form['lpubelts']:
            lpubelts = False
        else:
            lpubelts = request.form['lpubelts']
        final_imgs = []
        for file_key in request.files:
            file = request.files[file_key]
            if file.filename != '':
                filename = f"img_{next_id()}_{generate_random_string(8)}_{secure_filename(file.filename)}"
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                final_imgs.append("/image/" + filename)
        add_listing(res["token"], request.form['title'], float(request.form['price']), request.form['desc'], final_imgs, int(request.form['quantity']), currency=request.form['currency'], condition=request.form['condition'], lpubelts=lpubelts)
        notify_followers(res["username"], f"{res['username']} posted a new listing: {request.form['title']}", href="/listing/" + str(next_id() - 1))
        return redirect("/profile#listings")

@seller_blueprint.route('/seller/apply', methods=['GET', 'POST'])
def seller_apply():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/seller/apply"))
    if request.method == 'GET':
        return render_template('apply.html')
    else:
        for username, user in users.items():
            if user["admin"]:
                send_notif(username, f"New seller application from {res['username']} - {request.form['reputation']}", href=f"/user/{res['username']}")
        return render_template('apply.html', success=True)

@seller_blueprint.route('/seller/user/<name>')
def seller_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    user = get_user(name)
    if res:
        following = is_following(res["username"], name)
        is_self = res["username"] == name
    else:
        following = None
        is_self = False
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    if not user["approved_seller"]:
        return render_template('error.html', error="User is not approved as a seller", status_code="404"), 404
    rating = calc_rating(user["seller_rating"])
    listings = get_listings(name)
    tableview = request.args.get('tableview', 'on')
    use_tableview = tableview == 'on'
    return render_template('seller_user.html', user=user, name=name, listings=listings, rating=rating, currency_symbols=currency_symbols, tableview=use_tableview, following=following, is_self=is_self, authed=res)

@seller_blueprint.route('/seller/import', methods=['GET', 'POST'])
def seller_import():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/seller/import"))
    if request.method == 'GET':
        if not res["approved_seller"]:
            return render_template('error.html', error="Not authorized", status_code="401"), 401
        return render_template('import.html', default_currency=res["currency"], currencies=currencies)
    else:
        data = json.loads(request.form["json_data"])
        data["unlisted_style"] = "quantity"
        import_id = generate_random_string(128)
        imports[import_id] = "running"
        threading.Thread(target=sheet_import, args=(data, import_id)).start()
        return redirect("/seller/import/status/" + import_id)

@seller_blueprint.route('/seller/import/status/<import_id>', methods=['GET', 'POST'])
def task_status(import_id):
    status = imports.get(import_id, "Not started")
    if status == "running":
        return render_template('loading.html', refresh_rate=5)
    else:
        res = authed(request.cookies.get('token_DO_NOT_SHARE'))
        if not res:
            return redirect("/login?redir=" + urlencode("/seller/import/status/" + import_id))
        new_listings, errors = status
        fixed_listings = []
        for listing in new_listings:
            listing["id"] = 999999999
            listing["seller"] = res["username"]
            i = 0
            for image in listing["imgs"]:
                if "imgur.com" in image:
                    listing["imgs"][i] = image.replace(".jpg", ".jpeg").replace("https://i.imgur.com/", "/imgur/")
                i += 1
            fixed_listings.append(listing)
        if request.method == 'POST':
            # import the listings
            for listing in fixed_listings:
                listing["id"] = next_id()
                listings.append(listing)
            notify_followers(res["username"], f"{res['username']} imported {len(fixed_listings)} listings!", href="/seller/user/" + urlencode(res["username"]))
            return redirect("/profile#listings")
        return render_template('import_complete.html', listings=localize_prices(new_listings, user_currency=res["currency"]), errors=errors, currency_symbols=currency_symbols, user_currency=res["currency"])
