from flask import Blueprint, request

from common.auth_util import authed
from common.browse_util import localize_prices, remove_closed, sort_by_trending
#from serve import *
from common.currency import currency_symbols
from common.data import listings
from common.render import render_template

base_blueprint = Blueprint('base_blueprint', __name__,
                        template_folder='templates')

@base_blueprint.route('/')
def index():
    trending_listings = sort_by_trending(remove_closed(listings))[0:4]
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        user_currency = "USD"
    else:
        user_currency = res["currency"]
    localized = localize_prices(trending_listings, user_currency=user_currency)
    return render_template('index.html', trending_listings=localized, currency_symbols=currency_symbols, user_currency=user_currency)

@base_blueprint.route('/about')
def about():
    return render_template('about.html')

@base_blueprint.route('/privacy')
def privacy():
    return render_template('privacy.html')

@base_blueprint.route('/tos')
def tos():
    return render_template('tos.html')