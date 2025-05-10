import logging

from flask import request, Flask, Response
import create
import utils

app = Flask(__name__)

@app.route('/start')
def start():
    ak_id = request.headers['x-fc-access-key-id']
    ak_secret = request.headers['x-fc-access-key-secret']
    security_token = request.headers['x-fc-security-token']
    force = request.args.get('force')
    print(ak_id, ak_secret, security_token)
    client = utils.get_aliyun_client('eci', ak_id, ak_secret, security_token)
    status = create.create_container_group(client, force)
    return Response(status=status)

if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8000, debug=False)