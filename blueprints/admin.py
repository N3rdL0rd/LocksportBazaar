import json

from flask import Blueprint, redirect, request

from common.auth_util import authed
from common.data import reload_all, users, listings, wtb_listings
from common.render import render_template
from common.user_util import get_user, save_users, change_password
from common.util import urlencode, generate_random_string
from common.listing_util import get_listing, _close_listing

admin_blueprint = Blueprint('admin_blueprint', __name__,
                        template_folder='templates')

@admin_blueprint.route('/admin')
def admin():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    proc_users = []
    for k, v in users.items():
        # add username as a field
        proc_users.append({"username": k, **v})
    return render_template('admin.html', users=proc_users)

@admin_blueprint.route('/admin/user/<name>')
def admin_user(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    return render_template('admin_user.html', user=user, name=name)

@admin_blueprint.route('/admin/authorize/<name>')
def admin_authorize(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    users[name]["approved_seller"] = True
    save_users()
    return redirect("/admin")

@admin_blueprint.route('/admin/deauthorize/<name>')
def admin_deauthorize(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    users[name]["approved_seller"] = False
    save_users()
    return redirect("/admin")

@admin_blueprint.route('/admin/delete/<name>')
def admin_delete(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    del users[name]
    # now delete all listings by this user
    for i in range(len(listings)):
        if listings[i]["seller"] == name:
            del listings[i]
    for i in range(len(wtb_listings)):
        if wtb_listings[i]["seller"] == name:
            del wtb_listings[i]
    save_users()
    return redirect("/admin")

@admin_blueprint.route('/admin/reload_db')
def admin_reload_db():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    reload_all()
    return redirect("/admin")

@admin_blueprint.route('/admin/recover/<name>')
def admin_recover(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    return render_template("admin_recover.html", user=user, name=name)

@admin_blueprint.route('/admin/recover/<name>/random')
def admin_random(name):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    user = get_user(name)
    if not user:
        return render_template('error.html', error="User not found", status_code="404"), 404
    new_password = generate_random_string(16)
    change_password(name, new_password)
    return render_template("admin_recover.html", user=user, name=name, new_password=new_password)

@admin_blueprint.route('/admin/listing/<id>')
def admin_listing(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    listing = get_listing(int(id))
    if not listing:
        return render_template('error.html', error="Listing not found", status_code="404"), 404
    return render_template('admin_listing.html', listing=listing)

@admin_blueprint.route('/admin/listing/close/<id>')
def admin_close_listing(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    listing = get_listing(int(id))
    if not listing:
        return render_template('error.html', error="Listing not found", status_code="404"), 404
    _close_listing(int(id))
    return redirect('/admin/listing/' + id)

@admin_blueprint.route('/admin/listing/delete/<id>')
def admin_delete_listing(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/admin"))
    if not res["admin"]:
        return render_template('error.html', error="Not authorized", status_code="401"), 401
    listing = get_listing(int(id))
    if not listing:
        return render_template('error.html', error="Listing not found", status_code="404"), 404
    for i in range(len(listings)):
        if listings[i]["id"] == int(id):
            del listings[i]
            break
    return redirect('/admin/listing/' + id)
