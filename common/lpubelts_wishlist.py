import requests

from common.data import lpubelts_token

class TokenError(Exception):
    pass

class UserError(Exception):
    pass

def get_wishlist(id):
    url = f"https://explore.lpubelts.com/wishlist/?token={lpubelts_token}&id={id}"
    response = requests.get(url)
    data = response.json()[1]
    if 'status' in data and data['status'] == '200 OK':
        return data['wishlist']
    elif 'status' in data and data['status'] == '401 Unauthorized':
        raise TokenError('Unauthorized!')
    elif 'status' in data and data['status'] == '418 No Such User':
        raise UserError('No such user!')
    else:
        raise Exception('Unknown error!')