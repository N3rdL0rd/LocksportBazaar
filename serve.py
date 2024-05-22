from flask import Flask
from asgiref.wsgi import WsgiToAsgi
import datetime
import babel.dates
import uvicorn
from flask_cors import CORS
import requests
import json

from common.constants import DEBUG
from common.render import render_template
from common.data import users, listings, wtb_listings

app = Flask(__name__)
CORS(app)

if __name__ == '__main__':
    from blueprints.admin import admin_blueprint
    from blueprints.base import base_blueprint
    from blueprints.content import content_blueprint
    from blueprints.listings import listings_blueprint
    from blueprints.profile import profile_blueprint
    from blueprints.push import push_blueprint
    from blueprints.seller import seller_blueprint
    from blueprints.wtb import wtb_blueprint
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(base_blueprint)
    app.register_blueprint(content_blueprint)
    app.register_blueprint(listings_blueprint)
    app.register_blueprint(profile_blueprint)
    app.register_blueprint(push_blueprint)
    app.register_blueprint(seller_blueprint)
    app.register_blueprint(wtb_blueprint)

@app.template_filter()
def format_datetime(value, format='medium'):
    # value is a string formatted with isoformat()
    if format == 'full':
        format="EEEE, d. MMMM y 'at' HH:mm"
    elif format == 'medium':
        format="EE dd.MM.y HH:mm"
    elif format == 'small':
        format="dd.MM.y"
    dt = datetime.datetime.fromisoformat(value)
    return babel.dates.format_datetime(dt, format)

@app.errorhandler(404)
def not_found(path):
    return render_template('error.html', error="Not found", status_code="404"), 404

@app.errorhandler(500)
def internal_error():
    return render_template('error.html', error="Internal server error", status_code="500"), 500

asgi_app = WsgiToAsgi(app)

if __name__ == '__main__':
    if DEBUG:
        app.jinja_env.auto_reload = True
        app.config['TEMPLATES_AUTO_RELOAD'] = True
        app.run(host='0.0.0.0', debug=False)
    else:
        uvicorn.run("serve:asgi_app", port=80, log_level="info")
    print("Shutting down...")
    users.close()
    listings.close()
    wtb_listings.close()
