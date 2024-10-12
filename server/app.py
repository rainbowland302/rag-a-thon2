import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from core.main import get_response

app = Flask(__name__)

@app.route('/')
def hello_world():
    app.logger.info('Accessing root route')
    return 'Hello World!'

@app.route('/api/search', methods=['POST'])
def search():
    app.logger.info('Accessing search route')
    data = request.get_json()
    message = data.get('message')
    response = get_response(message)
    return jsonify({
        "msg": message,
        "res": response
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Changed port to 5001
