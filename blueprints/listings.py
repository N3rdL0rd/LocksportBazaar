from flask import Blueprint, request, redirect
from rapidfuzz import fuzz

from common.auth_util import authed
from common.browse_util import *
from common.constants import PAGE_LENGTH
from common.currency import currency_symbols
from common.data import all_mechanisms, listings
from common.listing_util import log_listing_view
from common.render import render_template
from common.user_util import get_user, wishlist, unwishlist, wished
from common.util import queryencode, urlencode
from common.wish_notify import get_all_listings

listings_blueprint = Blueprint('listings_blueprint', __name__,
                        template_folder='templates')

@listings_blueprint.route('/listings')
def show_listings():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        user_currency = "USD"
    else:
        user_currency = res["currency"]
    sort = request.args.get('sort', 'trending')
    if sort == "trending":
        sorted_listings = sort_by_trending(listings)
    elif sort == "top":
        sorted_listings = sort_by_views(listings)
    elif sort == "newest":
        sorted_listings = sort_by_newest(listings)
    elif sort == "oldest":
        sorted_listings = listings
    elif sort == "price_asc":
        sorted_listings = sort_by_price(localize_prices(listings, user_currency=user_currency))
    elif sort == "price_desc":
        sorted_listings = list(reversed(sort_by_price(localize_prices(listings, user_currency=user_currency))))
    pagenum = int(request.args.get('page', 1))
    page_listings = paginate(sorted_listings, pagenum, PAGE_LENGTH)
    show_forward = len(page_listings) == PAGE_LENGTH
    show_back = pagenum > 1
    return render_template('listings.html', listings=localize_prices(page_listings, user_currency=user_currency), orig_listings=page_listings, next_page=pagenum+1, prev_page=pagenum-1, page=pagenum, show_forward=show_forward, show_back=show_back, user_currency=user_currency, currency_symbols=currency_symbols, sort=sort)

@listings_blueprint.route('/listings/<lpubelts>')
def show_listings_lpubelts(lpubelts):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    use_listings = get_all_listings(lpubelts)
    if not res:
        user_currency = "USD"
    else:
        user_currency = res["currency"]
    sort = request.args.get('sort', 'trending')
    if sort == "trending":
        sorted_listings = sort_by_trending(use_listings)
    elif sort == "top":
        sorted_listings = sort_by_views(use_listings)
    elif sort == "newest":
        sorted_listings = sort_by_newest(use_listings)
    elif sort == "oldest":
        sorted_listings = use_listings
    elif sort == "price_asc":
        sorted_listings = sort_by_price(localize_prices(use_listings, user_currency=user_currency))
    elif sort == "price_desc":
        sorted_listings = list(reversed(sort_by_price(localize_prices(use_listings, user_currency=user_currency))))
    pagenum = int(request.args.get('page', 1))
    page_listings = paginate(sorted_listings, pagenum, PAGE_LENGTH)
    show_forward = len(page_listings) == PAGE_LENGTH
    show_back = pagenum > 1
    return render_template('listings.html', listings=localize_prices(page_listings, user_currency=user_currency), orig_listings=page_listings, next_page=pagenum+1, prev_page=pagenum-1, page=pagenum, show_forward=show_forward, show_back=show_back, user_currency=user_currency, currency_symbols=currency_symbols, sort=sort)


@listings_blueprint.route('/search')
def search_listings():
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        user_currency = "USD"
    else:
        user_currency = res["currency"]
    min_price = int(request.args.get('min_price', '0'))
    max_price = int(request.args.get('max_price', '999999999'))
    sort = request.args.get('sort', 'trending')
    query = request.args.get('query', '')
    request_query = request.args.copy()
    results = []
    if query.strip() == '':
        results = listings
    else:
        for listing in listings:
            ratio = fuzz.WRatio(query.lower(), listing["title"].lower())
            if ratio >= 80:
                results.append(listing)
    query_base = "&min_price=" + str(min_price) + "&max_price=" + str(max_price)
    if request.args.get('belt') and request.args.get('belt') != "none":
        results = filter_belt(results, request.args.get('belt'))
        query_base += "&belt=" + queryencode(request.args.get('belt'))
    if request.args.get('mechanism') and request.args.get('mechanism') != "none":
        results = filter_mechanism(results, [request.args.get('mechanism')])
        query_base += "&mechanism=" + queryencode(request.args.get('mechanism'))
    if request.args.get('location') and request.args.get('location') != "none":
        results = filter_approx_location(results, request.args.get('location'))
        query_base += "&location=" + queryencode(request.args.get('location'))
    if request.args.get('brand') and request.args.get('brand') != "none":
        results = filter_brand(results, request.args.get('brand'))
        query_base += "&brand=" + queryencode(request.args.get('brand'))
    if request.args.get('show_closed', 'off') == 'on':
        show_all = True
        query_base += "&show_closed=on"
    else:
        show_all = False
        query_base += "&show_closed=false"
    if sort == "trending":
        sorted_listings = sort_by_trending(results)
    elif sort == "top":
        sorted_listings = sort_by_views(results)
    elif sort == "newest":
        sorted_listings = sort_by_newest(results)
    elif sort == "oldest":
        sorted_listings = results
    elif sort == "price_asc":
        sorted_listings = sort_by_price(localize_prices(results, user_currency=user_currency))
    elif sort == "price_desc":
        sorted_listings = list(reversed(sort_by_price(localize_prices(results, user_currency=user_currency))))
    pagenum = int(request.args.get('page', 1))
    page_listings = paginate(sorted_listings, pagenum, PAGE_LENGTH, ignore_closed=not show_all)
    show_forward = len(page_listings) == PAGE_LENGTH
    show_back = pagenum > 1
    return render_template('search.html',
                           listings=localize_prices(page_listings, user_currency=user_currency),
                           orig_listings=page_listings,
                           next_page=pagenum+1,
                           prev_page=pagenum-1,
                           page=pagenum,
                           show_forward=show_forward,
                           show_back=show_back,
                           user_currency=user_currency,
                           currency_symbols=currency_symbols,
                           sort=sort,
                           query=query,
                           belt=request_query.get('belt'),
                           mechanisms=all_mechanisms,
                           selected_mechanism=request_query.get('mechanism'),
                           locations=valid_general_locations,
                           selected_location=request_query.get('location'),
                           brands=all_brands,
                           selected_brand=request_query.get('brand'),
                           query_base=query_base,
                           max_price=max_price,
                           min_price=min_price,
                           show_all=show_all)

@listings_blueprint.route('/listing/<int:id>')
def show_listing(id):
    log_listing_view(id)
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        user_currency = "USD"
    else:
        user_currency = res["currency"]
    show_wished = False
    is_wished = False
    for listing in listings:
        if listing["id"] == id:
            if res:
                show_wished = True
                is_wished = wished(res["username"], listing['lpubelts']) or wished(res["username"], listing['id'])
            return render_template('listing.html', listing=fix_newline(localize_price(listing, user_currency=user_currency)), user_currency=user_currency, currency_symbols=currency_symbols, seller=get_user(listing["seller"]), show_wished=show_wished, is_wished=is_wished)
    return render_template('listing.html', error="Listing not found")

@listings_blueprint.route('/listing/<int:id>/wishlist')
def wishlist_listing(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/listing/" + str(id) + "/wishlist"))
    res_listing = None
    for listing in listings:
        if listing["id"] == id:
            res_listing = listing
            break
    if not res_listing:
        return render_template('error.html', error="Listing not found", status_code="404")
    if not res_listing['lpubelts']:
        wishlist(res["username"], listing['id'])
    else:
        wishlist(res["username"], listing['lpubelts'])
    return redirect("/listing/" + str(id))

@listings_blueprint.route('/listing/<int:id>/unwishlist')
def unwishlist_listing(id):
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/listing/" + str(id) + "/unwishlist"))
    res_listing = None
    for listing in listings:
        if listing["id"] == id:
            res_listing = listing
            break
    if not res_listing:
        return render_template('error.html', error="Listing not found", status_code="404")
    if not res_listing['lpubelts']:
        unwishlist(res["username"], listing['id'])
    else:
        unwishlist(res["username"], listing['lpubelts'])
    return redirect("/listing/" + str(id))

@listings_blueprint.route('/listing/unwishlist/<id>')
def unwishlist_listing_direct(id):
    # like the other ones, but directly unwishlists the lpubelts id
    res = authed(request.cookies.get('token_DO_NOT_SHARE'))
    if not res:
        return redirect("/login?redir=" + urlencode("/listing/unwishlist/" + str(id)))
    unwishlist(res["username"], id)
    return redirect("/listing/" + str(id))