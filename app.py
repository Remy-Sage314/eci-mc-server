from flask import request, Flask, Response
import create
import utils

app = Flask(__name__)

@app.route('/start')
def start():
    ak_id = request.headers['x-fc-access-key-id']
    ak_secret = request.headers['x-fc-access-key-secret']
    client = utils.get_aliyun_client('eci', ak_id, ak_secret)
    force = request.args.get('force')
    status = create.create_container_group(client, force)
    return Response(status=status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)