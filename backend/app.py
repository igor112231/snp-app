#nadal jest error - wychwytuje error i na stronie wyświetla komunikat ale jest to najprawdopodobniej przez niezgodną wersję
# sekwencje przesyłają się do backendu poprawnie
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

app = Flask(__name__)
CORS(app) 
socketio = SocketIO(app)

# Konfiguracja logowania
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/api/analyze', methods=['POST'])
def analyze():
    logger.debug("Received request for analysis")
    data = request.get_json()
    
    if not data:
        logger.error("No data provided")
        return jsonify({'error': 'No data provided'}), 400

    mutant_sequence = data.get('mutantSequence')
    wild_sequence = data.get('wildSequence')
    logger.debug(f"Mutant sequence: {mutant_sequence}, Wild sequence: {wild_sequence}")

    # Możesz emitować wiadomość do klientów WebSocket
    socketio.emit('analysis_started', {'mutantSequence': mutant_sequence, 'wildSequence': wild_sequence})

    response = {'result': 'Analysis started', 'mutantSequence': mutant_sequence, 'wildSequence': wild_sequence}
    logger.debug(f"Response: {response}")
    return jsonify(response), 200

@socketio.on('connect')
def handle_connect():
    logger.debug("Client connected")
    emit('response', {'data': 'Connected to WebSocket'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)