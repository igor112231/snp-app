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

# Allow CORS from the frontend origin
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")  # Allow socket connections from frontend

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Directory where app.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_pipeline(mutant_sequence, wild_sequence):
    # Generate a unique ID
    analysis_id = str(uuid.uuid4())
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)

    # Save sequences to files
    os.makedirs(pipeline_dir, exist_ok=True)

    wt_file_path = os.path.join(pipeline_dir, 'wt.txt')
    mut_file_path = os.path.join(pipeline_dir, 'mut.txt')

    with open(wt_file_path, 'w') as wt_file:
        wt_file.write(wild_sequence)
    with open(mut_file_path, 'w') as mut_file:
        mut_file.write(mutant_sequence)

    # Set file permissions
    for file_path in [wt_file_path, mut_file_path]:
        os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IROTH | stat.S_IWOTH)

    logger.debug(f"WT file path: {wt_file_path}")
    logger.debug(f"Mut file path: {mut_file_path}")
    logger.debug(f"Files in PIPELINE_DIR: {os.listdir(pipeline_dir)}")
    
    try:
        # Run analyses
        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '01-RNApdist'), pipeline_dir], check=True)
        
        # Read RNApdist result
        with open(os.path.join(pipeline_dir, 'RNApdist-result.txt'), 'r') as f:
            rnapdist_result = f.read().strip()
        logger.debug(f"RNApdist result: {rnapdist_result}")

        # Run the remaining analyses
        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '02-RNAfold'), pipeline_dir], check=True)
        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '03-RNAdistance'), pipeline_dir], check=True)
        subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '04-RNAplot'), pipeline_dir], check=True)

        # Send the result via WebSocket
        socketio.emit('analysis_completed', {
            'rnapdist_result': rnapdist_result,
            'analysisId': analysis_id
        })

    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline failed: {e}")
        socketio.emit('analysis_failed', {'error': str(e), 'analysisId': analysis_id})

# Endpoint to start analysis
@socketio.on('analyze')
def analyze(data):
    logger.debug("Received request for analysis")
    
    if not data:
        logger.error("No data provided")
        emit('analysis_failed', {'error': 'No data provided'})
        return

    mutant_sequence = data.get('mutantSequence')
    wild_sequence = data.get('wildSequence')
    logger.debug(f"Mutant sequence: {mutant_sequence}, Wild sequence: {wild_sequence}")

    socketio.emit('analysis_started')
    # Analyze in the background
    threading.Thread(target=run_pipeline, args=(mutant_sequence, wild_sequence)).start()

    # Response for the client
    socketio.emit('analysis_completed', {'result': 'Analysis started', 'analysisId': str(uuid.uuid4())})

@socketio.on('connect')
def handle_connect():
    logger.debug("Client connected")
    emit('response', {'data': 'Connected to WebSocket'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
