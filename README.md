# LocksportBazaar

> hi mgsecure

A marketplace for organizing informal deals for the [locksport](https://en.wikipedia.org/wiki/Locksport) community - based on LPU's Bazaar, but like, web based and stuff.

## Installation

One-liner (Linux): `python3 -m venv env && source ./env/bin/activate && pip install -r requirements.txt && python serve.py`

For Windows: `python -m venv env && env\Scripts\activate && pip install -r requirements.txt && python serve.py`

> [!NOTE]  
> This *should* work for most things, but features that are dependent on the Google API, the Imgur API, and the LPUBelts Wishlist API won't work out of the box.

If you want access to all features, you'll also need a service account from a Google Cloud project with access to the Google Docs API. Export it and put it in a JSON file in `./data/token.json` in this format:

```json
{
    "type": "service_account",
    "project_id": "<your project id",
    "private_key_id": "<private key id>",
    "private_key": "<private key>",
    "client_email": "<your project email>",
    "client_id": "<your project id>",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "<your cert url>",
    "universe_domain": "googleapis.com"
}
```

In order to import wishlists from LPUBelts, you'll also need a token for the LPUBelts Wishlist API for the wishlist import feature. Put it in `./data/lpubelts_token.txt`. In order to get one, you'll need to contact [lpubeltapp@gmail.com](mailto:lpubeltapp@gmail.com).

For the Imgur API, you'll need to set up an application and get a client ID. Put it in `./data/imgur_client_id.txt` in the format `Client-ID XXXXXXXXXXXXXXXX`.

## In Production

- Edit `./common/constants.py`
- Set `VERSION` to a desired value
- Verify that `DEBUG` is set to `False`
- Clear any testing data from `./data` and `./user_content`
- `$ python serve.py`
