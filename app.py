import logging
import time

from flask import request, Flask, Response
import create
import utils
from dingtalk import get_sign

app = Flask(__name__)

@app.route('/start')
def start():
    ak_id = request.headers['x-fc-access-key-id']
    ak_secret = request.headers['x-fc-access-key-secret']
    security_token = request.headers['x-fc-security-token']
    force = request.args.get('force')
    print(ak_id, ak_secret, security_token)
    client = utils.get_ali_client('eci', ak_id, ak_secret, security_token)
    status = create.create_container_group(client, force)
    return Response(status=status)

@app.route('/stop')
def stop():
    ...

@app.route('ding_receive', methods=['POST'])
def receive_dingtalk():
    now = round(time.time() * 1000)
    timestamp = request.headers['timestamp']
    if get_sign(timestamp) != request.headers['sign'] or (abs(int(timestamp) - now)) > 600000:
        return Response(status=403)
    msg = request.json['text']
    if '开' in msg:
        return start()
    elif '关' in msg:
        return stop()
    else:
        return Response(status=400)


if __name__ == '__main__':
    app.logger.setLevel(logging.DEBUG)
    app.run(host='0.0.0.0', port=8000, debug=False)