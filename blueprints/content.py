from PIL import Image
from io import BytesIO
import os

import requests
from flask import Blueprint, send_file, send_from_directory

from common.constants import UPLOAD_FOLDER

content_blueprint = Blueprint('content_blueprint', __name__,
                        template_folder='templates')

if not os.path.exists('./user_content'):
    os.makedirs('./user_content')

@content_blueprint.route("/image/<image>")
def post_image(image):
    return send_from_directory(UPLOAD_FOLDER, image)

@content_blueprint.route("/imgur/<id>")
def imgur(id):
    cache_dir = './user_content'
    cache_file = f"{cache_dir}/{id}.jpeg"

    # Check if image is in cache
    if os.path.exists(cache_file):
        return send_file(cache_file, mimetype='image/jpeg')

    # If not in cache, retrieve from Imgur
    url = f"https://i.imgur.com/{id}"
    headers = {'Referer': '', 'User-Agent': ''}
    response = requests.get(url, headers=headers, stream=True)

    if response.status_code != 200:
        return "Image not found", 404

    # Save image to cache
    image = Image.open(BytesIO(response.content))
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    image.save(cache_file)

    return send_file(BytesIO(response.content), mimetype='image/jpeg')