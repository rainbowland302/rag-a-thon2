from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/search', methods=['POST'])
def search():
    data = request.get_json()
    message = data.get('message')
    response = {
        "msg": message,
        "res": "Here is your ans"
    }
    return jsonify(response)


if __name__ == '__main__':
    app.run()
