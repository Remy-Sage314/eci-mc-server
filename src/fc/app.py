# -*- coding: utf-8 -*-
from os import environ

from flask import request, Flask, Response

from fc import create_container
import utils


app = Flask(__name__)

ACCESS_KEY_ID = environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID')
ACCESS_KEY_SECRET = environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
SECURITY_TOKEN = environ.get('ALIBABA_CLOUD_SECURITY_TOKEN')

@app.route('/start')
def start():
    force = request.args.get('force')
    version = request.args.get('version')

    client = utils.get_ali_client('eci', ACCESS_KEY_ID, ACCESS_KEY_SECRET, SECURITY_TOKEN)
    status = create_container.create_container_group(client, version, force)
    return Response(status=status)

@app.route('/stop')
def stop():
    ...

if __name__ == '__main__':
    app.logger.info(ACCESS_KEY_ID, ACCESS_KEY_SECRET,  SECURITY_TOKEN)
    app.run(host='0.0.0.0', port=9000, debug=False)
