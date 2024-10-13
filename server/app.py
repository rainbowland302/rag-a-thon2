import sys
import os
from flask import Flask, request, jsonify, send_from_directory
from core.pinecone_steam import get_response
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

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
    app.run(debug=True, host='0.0.0.0', port=5001)
