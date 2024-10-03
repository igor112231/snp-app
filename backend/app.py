from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
import subprocess
import threading
import os
import uuid
import stat

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

# Konfiguracja logow
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Uruchamiane pipeline
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # katalog, w którym jest app.py

def run_pipeline(mutant_sequence, wild_sequence):
    # Generowanie unikalnego ID
    analysis_id = str(uuid.uuid4())
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)

    # Zapis sekwencji do plików
    os.makedirs(pipeline_dir, exist_ok=True)

    wt_file_path = os.path.join(pipeline_dir, 'wt.txt')
    mut_file_path = os.path.join(pipeline_dir, 'mut.txt')

    with open(wt_file_path, 'w') as wt_file:
        wt_file.write(wild_sequence)
    with open(mut_file_path, 'w') as mut_file:
        mut_file.write(mutant_sequence)

    os.chmod(wt_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)
    os.chmod(mut_file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

    logger.debug(f"WT file path: {wt_file_path}")
    logger.debug(f"Mut file path: {mut_file_path}")
    logger.debug(f"Files in PIPELINE_DIR: {os.listdir(pipeline_dir)}")
    logger.debug(f"Pipeline directory: {pipeline_dir}")

    try:
        # Uruchomienie analiz
        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '01-RNApdist'), pipeline_dir], check=True)
        
        # Na razie jedynie wyniki RNApdist wyswietlane
        with open(os.path.join(pipeline_dir, 'RNApdist-result.txt'), 'r') as f:
            rnapdist_result = f.read().strip()
        logger.debug(f"RNApdist result: {rnapdist_result}")

        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '02-RNAfold'), pipeline_dir], check=True)

        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '03-RNAdistance'), pipeline_dir], check=True)

        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '04-RNAplot'), pipeline_dir], check=True)

        # Wysłanie wyniku przez WebSocket
        socketio.emit('analysis_completed', {
            'rnapdist_result': rnapdist_result,
            'analysisId': analysis_id
        })

    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline failed: {e}")
        socketio.emit('analysis_failed', {'error': str(e), 'analysisId': analysis_id})

# Endpoint do rozpoczęcia analizy
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

    # Analiza w tle
    threading.Thread(target=run_pipeline, args=(mutant_sequence, wild_sequence)).start()

    # unikalne ID dla analizy
    response = {'result': 'Analysis started', 'analysisId': str(uuid.uuid4())}
    logger.debug(f"Response: {response}")
    return jsonify(response), 200

@socketio.on('connect')
def handle_connect():
    logger.debug("Client connected")
    emit('response', {'data': 'Connected to WebSocket'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
