import datetime
import json

from flask import Blueprint, redirect, request

from common.auth_util import authed
from common.browse_util import paginate
from common.constants import PAGE_LENGTH
from common.data import wtb_listings
from common.render import render_template
from common.user_util import send_notif
from common.util import urlencode

wtb_blueprint = Blueprint('wtb_blueprint', __name__,
                        template_folder='templates')

@wtb_blueprint.route('/wtb')
def wtb():
    processed_listings = []
    reversed_listings = list(reversed(wtb_listings))
    for listing in reversed_listings:
        if listing["open"]:
            processed_listings.append(listing)
    page = int(request.args.get('page', 1))
    processed_listings = paginate(processed_listings, page, PAGE_LENGTH)
    show_forward_button = len(processed_listings) == PAGE_LENGTH
    show_back_button = page > 1
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return render_template('wtb.html', posts=processed_listings, authed=False, show_forward=show_forward_button, show_back=show_back_button, pagenum=page)
    return render_template('wtb.html', posts=processed_listings, authed=True, user=res, show_forward=show_forward_button, show_back=show_back_button, pagenum=page)

@wtb_blueprint.route('/wtb/close/<id>', methods=['GET', 'POST'])
def wtb_close(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/wtb"))
    for post in wtb_listings:
        if post["id"] == int(id):
            if post["poster"] == res["username"] or res["admin"]:
                post["open"] = False
                return redirect("/wtb")
    return render_template('error.html', error="Post not found", status_code="404"), 404

@wtb_blueprint.route('/wtb/new', methods=['GET', 'POST'])
def wtb_new():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/wtb/new"))
    if request.method == 'GET':
        return render_template('wtb_new.html')
    else:
        wtb_listings.append({"title": request.form['title'], "body": request.form['body'], "poster": res["username"], "lpubelts": request.form["lpubelts"], "open": True, "id": len(wtb_listings) + 1, "comments": []})
        return redirect("/wtb")

@wtb_blueprint.route('/wtb/<id>', methods=['GET', 'POST'])
def wtb_post(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if request.method == 'POST':
        # create comment on post
        if not res:
            return redirect("/login?redir=" + urlencode("/wtb/" + id))
        for post in wtb_listings:
            if post["id"] == int(id):
                post["comments"].append({"poster": res["username"], "body": request.form['body'], "date": datetime.datetime.now().isoformat()})
                if post["poster"] != res['username']:
                    send_notif(post["poster"], f"New comment on your WTB post from {res['username']}!", href=f"/wtb/{id}")
    for post in wtb_listings:
        if post["id"] == int(id):
            if res:
                return render_template('wtb_post.html', post=post, user=res, authed=True)
            return render_template('wtb_post.html', post=post, authed=False)
    return render_template('error.html', error="Post not found", status_code="404"), 404