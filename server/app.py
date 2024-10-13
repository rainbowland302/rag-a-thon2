import sys
import os
from flask import Flask, request, jsonify
from core.pinecone_steam import get_response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)


@app.route('/api/search', methods=['POST'])
def search():
    app.logger.info('Accessing search route')
    data = request.get_json()
    message = data.get('message')
    response = get_response(message)
    return jsonify({
        "msg": message,
        "res": response.get('res'),
        "img": response.get('img')
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changed host to '0.0.0.0' for VESSL deployment
