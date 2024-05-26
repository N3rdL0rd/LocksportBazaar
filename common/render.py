import datetime

from flask import render_template as _render_template
from flask import request

from common.auth_util import authed
from common.data import locks
from common.constants import VERSION

nav_items = [
    {'href': '/', 'caption': 'Home'},
    {'href': '/search', 'caption': 'Search'},
    {'href': '/listings', 'caption': 'Listings'},
    {'href': '/wtb', 'caption': 'WTB'},
    {'href': '/profile', 'caption': 'Profile'},
]

footer_items = [
    {'href': 'https://github.com/N3rdL0rd/LocksportBazaar', 'caption': 'GitHub'},
    {'href': '/about', 'caption': 'About'},
    {'href': '/privacy', 'caption': 'Privacy'},
    {'href': '/tos', 'caption': 'Terms of Service'},
]

def render_template(template_name, **context):
    # we want to enable notifications if the user is authed
    token = request.cookies.get('token_DO_NOT_SHARE')
    if token:
        user = authed(token)
        if user:
            notifs = user["notifications"]
            shownotifs = True
            unreadnotifs = len([x for x in user["notifications"] if not x["read"]])
            isadmin = user["admin"]
        else:
            shownotifs = False
            notifs = []
            unreadnotifs = 0
            isadmin = False
    else:
        shownotifs = False
        notifs = []
        unreadnotifs = 0
        isadmin = False
    return _render_template(template_name, nav_items=nav_items, footer_items=footer_items, year=str(datetime.datetime.now().year), show_notifications=shownotifs, notifications=notifs, unread_notifications=unreadnotifs, isadmin=isadmin, locks=locks, version=VERSION, **context)
