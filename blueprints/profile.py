from flask import Blueprint, make_response, redirect, request

import bcrypt
import re

from common.auth_util import authed, login_user
from common.currency import (currencies, currency_symbols,
                             valid_general_locations)
from common.data import listings, users
from common.listing_util import get_listings
from common.render import render_template
from common.user_util import (calc_rating, create_user, follow, get_user,
                              is_following, mark_notifications_read,
                              notify_followers, send_notif, unfollow,
                              update_profile, change_password, wishlist)
from common.util import clamp, save_users, urlencode
from common.lpubelts_wishlist import get_wishlist
from common.wish_notify import get_wishlist_listings

profile_blueprint = Blueprint('profile_blueprint', __name__,
                        template_folder='templates')

@profile_blueprint.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.args.get('closed') == None:
        closed = False
    else:
        closed = True
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile"))
    if res["approved_seller"]:
        userlistings = get_listings(res["username"])
    else:
        userlistings = []
    res_normal, res_lpubelts = get_wishlist_listings(res)
    wishlist_seperate = []
    for item in res_normal:
        wishlist_seperate.append({
            "title": item["title"],
            "id": item["id"],
            "desc": item["desc"],
            "price": str(item["price"]),
            "currency": item["currency"],
            "quantity": item["quantity"]
        })
    wishlist_lpubelts = []
    for item in res_lpubelts:
        wishlist_lpubelts.append({
            "title": item[0]["makeModels"][0]["make"] + " " + item[0]["makeModels"][0]["model"],
            "id": item[0]["id"],
            "quantity": len(item[1]),
            "belt": item[0]["belt"]
        })
    if request.method == 'POST':
        form = dict(request.form)
        for field, value in form.items():
            if value == "None":
                form[field] = None
        update_profile(res["token"], form['discord'], form['email'], form['name'], form['addie'], form['currency'], form['bio'], form['general_location'])
        return redirect("/profile")
    return render_template('profile.html', user=res, user_listings=userlistings, showclosed=closed, currencies=currencies, valid_locations=valid_general_locations, wishlist_seperate=wishlist_seperate, wishlist_lpubelts=wishlist_lpubelts)

@profile_blueprint.route('/profile/password', methods=['GET', 'POST'])
def password():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile/password"))
    if request.method == 'POST':
        if bcrypt.checkpw(request.form['current'].encode('utf-8'), res["password"].encode('utf-8')):
            if request.form['new'] != request.form['confirm']:
                return render_template('change_password.html', error='New password does not match confirmation!')
            change_password(res['username'], request.form['new'])
            
            return redirect("/logout")
        else:
            return render_template('change_password.html', error='Incorrect current password!')
    return render_template('change_password.html')


@profile_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        token = login_user(request.form['username'], request.form['password'])
        if token:
            res = make_response("<meta http-equiv='refresh' content='0;url=" + request.args.get('redir', '/') + "'>", 302)
            res.set_cookie('token_DO_NOT_SHARE', token)
            return res
        return render_template('login.html', error="Incorrect username or password")
    return render_template('login.html', redir=request.args.get('redir', '/'))

@profile_blueprint.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        for username, user in users.items():
            if user["admin"]:
                send_notif(username, f"New password recovery request for {request.form['username']}", href="/admin/recover/" + request.form['username'])
        return render_template('recovering.html')
    return render_template('forgot.html')

@profile_blueprint.route('/logout')
def logout():
    res = make_response("<meta http-equiv='refresh' content='0;url=" + request.args.get('redir', '/') + "'>", 302)
    res.set_cookie('token_DO_NOT_SHARE', '', expires=0)
    return res

@profile_blueprint.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        if create_user(request.form['username'], request.form['password']):
            token = login_user(request.form['username'], request.form['password'])
            if token:
                res = make_response("<meta http-equiv='refresh' content='0;url=/profile'>", 302)
                res.set_cookie('token_DO_NOT_SHARE', token)
                return res
            return render_template('login.html', error="Somehow something got messed up during account creation. How?!?")
        return render_template('signup.html', error="Username already taken")
    return render_template('signup.html')

@profile_blueprint.route('/user/<name>')
def show_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    rating = calc_rating(user["buyer_rating"])
    if res:
        following = is_following(res["username"], name)
        is_self = res["username"] == name
    else:
        following = None
        is_self = False
    return render_template('user.html', user=user, name=name, rating=rating, authed=res, following=following, is_self=is_self)

@profile_blueprint.route("/notifications")
def notifications():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/notifications"))
    mark_notifications_read(res["username"])
    return render_template('notifications.html')

@profile_blueprint.route('/contact/<id>', methods=['GET', 'POST'])
def contact_seller(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/contact/" + id))
    if request.method == 'GET':
        for listing in listings:
            if listing["id"] == int(id):
                return render_template('contact.html', listing=listing, currency_symbols=currency_symbols)
        return render_template('error.html', error="Listing not found", status_code="404")
    else:
        for listing in listings:
            if listing["id"] == int(id):
                send_notif(listing["seller"], f"New message from {res['username']}: {request.form['msg']}", href=f"/listing/{id}")
                return redirect("/listing/" + str(id))
        return render_template('error.html', error="Listing not found", status_code="404")

@profile_blueprint.route('/review/<name>', methods=['GET', 'POST'])
def review_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/review/" + name))
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    if request.method == 'GET':
        return render_template('review.html', user=user, name=name, type=request.args.get('type'))
    else:
        if request.form['type'] == "seller":
            rating = user["seller_rating"]
        else:
            rating = user["buyer_rating"]
        rating[res["username"]] = {"score": clamp(int(request.form['rating']), 0, 10), "comment": request.form['review']}
        save_users()
        
        return redirect("/user/" + name)

# TODO: seriously condense this section
@profile_blueprint.route('/user/<name>/follow')
def follow_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/user/" + name))
    follow(res["username"], name)
    return redirect("/user/" + name)

@profile_blueprint.route('/user/<name>/unfollow')
def unfollow_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/user/" + name))
    unfollow(res["username"], name)
    return redirect("/user/" + name)

@profile_blueprint.route('/seller/user/<name>/follow')
def seller_follow_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/user/" + name))
    follow(res["username"], name)
    return redirect("/seller/user/" + name)

@profile_blueprint.route('/seller/user/<name>/unfollow')
def seller_unfollow_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/user/" + name))
    unfollow(res["username"], name)
    return redirect("/seller/user/" + name)

@profile_blueprint.route('/profile/gdpr')
def gdpr():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile/gdpr"))
    data_listings = get_listings(res["username"])
    return render_template('gdpr.html', data_user=res, data_listings=data_listings)

@profile_blueprint.route('/profile/import', methods=['GET', 'POST'])
def import_wishlist():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/profile/import"))
    if request.method == 'POST':
        match = re.compile(r'https://lpubelts\.com/#/profile/([^?]*)').search(request.form.get('profile_url'))
        if match:
            user_wishlist = get_wishlist(match.group(1))
            try:
                for item in user_wishlist:
                    wishlist(res["username"], item) # TODO: validation on this? that's a lot of trust
            except Exception as e:
                return render_template('import_wishlist.html', user=res, error=str(e))
        else:
            return render_template('import_wishlist.html', user=res, error="Invalid profile URL")
        return redirect("/profile")
    return render_template('import_wishlist.html', user=res)
