import logging
from os import environ

from flask import request, Flask, Response
import create_container

import config
import utils

app = Flask(__name__)
CONFIG = config.load_config()
ACCESS_KEY_ID = environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
SECURITY_TOKEN = environ.get('ALIBABA_CLOUD_SECURITY_TOKEN')

@app.route('/start')
def start():
    force = request.args.get('force')
    sid = request.args.get('sid')

    client = utils.get_ali_client('eci', ACCESS_KEY_ID, ACCESS_KEY_SECRET, SECURITY_TOKEN)
    nas_mc_path = CONFIG.nas_path / 'servers' / sid if sid else CONFIG.nas_path / 'servers' / CONFIG.default_server
    status = create_container.create_container_group(client, nas_mc_path, force)
    return Response(status=status)

@app.route('/stop')
def stop():
    ...

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=9000, debug=True)
