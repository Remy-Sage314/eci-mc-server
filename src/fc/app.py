import logging
from os import environ

from flask import request, Flask, Response

from src.fc import create_container
import src.utils
import src.config


app = Flask(__name__)
CONFIG = src.config.load_config()
ACCESS_KEY_ID = environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
SECURITY_TOKEN = environ.get('ALIBABA_CLOUD_SECURITY_TOKEN')

@app.route('/start')
def start():
    force = request.args.get('force')
    sid = request.args.get('sid', CONFIG.default_server)

    client = src.utils.get_ali_client('eci', ACCESS_KEY_ID, ACCESS_KEY_SECRET, SECURITY_TOKEN)
    nas_mc_path = CONFIG.nas_path / 'servers' / sid
    status = create_container.create_container_group(client, nas_mc_path, force)
    return Response(status=status)

@app.route('/stop')
def stop():
    ...

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=9000, debug=True)
