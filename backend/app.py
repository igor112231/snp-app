from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
import subprocess
import threading
import os
import uuid
import shutil
import eventlet

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", path="/socket.io")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_pipeline(mutant_sequence, wild_sequence, analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)

    os.makedirs(pipeline_dir, exist_ok=True)
    wt_file_path = os.path.join(pipeline_dir, 'wt.txt')
    mut_file_path = os.path.join(pipeline_dir, 'mut.txt')

    with open(wt_file_path, 'w') as wt_file:
        wt_file.write(wild_sequence + '\n')
    with open(mut_file_path, 'w') as mut_file:
        mut_file.write(mutant_sequence + '\n')

    try:
        socketio.emit('task_status', {'analysis_id': analysis_id, 'status': "In progress"}, broadcast=True)

        try:
            subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '01-RNApdist')], cwd=pipeline_dir, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Step 01-RNApdist failed: {e}")
            socketio.emit('task_status', {'analysis_id': analysis_id, 'status': 'failed', 'step': '01-RNApdist', 'error': str(e)}, broadcast=True)
            return

        try:
            subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '02-RNAfold')], cwd=pipeline_dir, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Step 02-RNAfold failed: {e}")
            socketio.emit('task_status', {'analysis_id': analysis_id, 'status': 'failed', 'step': '02-RNAfold', 'error': str(e)}, broadcast=True)
            return

        try:
            subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '03-RNAdistance')], cwd=pipeline_dir, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Step 03-RNAdistance failed: {e}")
            socketio.emit('task_status', {'analysis_id': analysis_id, 'status': 'failed', 'step': '03-RNAdistance', 'error': str(e)}, broadcast=True)
            return

        #try:
        #    subprocess.run(['bash', os.path.join(BASE_DIR, 'pipeline', '04-RNAplot')], cwd=pipeline_dir, check=True)
        #except subprocess.CalledProcessError as e:
        #    logger.error(f"Step 04-RNAplot failed: {e}")
        #    socketio.emit('task_status', {'analysis_id': analysis_id, 'status': 'failed', 'step': '04-RNAplot', 'error': str(e)}, broadcast=True)
        #    return


        try:
            logger.debug(f"HITtree")
            subprocess.run(['python3', os.path.join(BASE_DIR, 'pipeline', 'tree.py'), pipeline_dir],check=True)
            logger.debug(f"After HITtree")
        except subprocess.CalledProcessError as e:
            logger.error(f"Step HIT tree failed: {e}")
            socketio.emit('task_status', {'analysis_id': analysis_id, 'status': 'failed', 'step': 'HITtree', 'error': str(e)}, broadcast=True)
            return

        socketio.emit('task_status', {'analysis_id': analysis_id, 'status': "Analysis completed"}, broadcast=True)


    #Pewnie gdzieś tutaj zapis do bazy danych, na razie nie ma danych z rnaplot - chociaż do nich i tak chyba zapisujemy tylko url endpointu

    except Exception as e:
        logger.error(f"Unexpected error in pipeline: {e}")
        socketio.emit('task_status', {'analysis_id': analysis_id, 'status': 'failed', 'error': 'unexpected error', 'details': str(e)}, broadcast=True)


    


@app.route('/api/analyze/pair', methods=['POST'])
def analyze_pair():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    mutant_sequence = data.get('mutantSequence')
    wild_sequence = data.get('wildSequence')
    logger.debug(f"Mutant sequence: {mutant_sequence}, Wild sequence: {wild_sequence}")
    
    if not wild_sequence or not mutant_sequence:
        return jsonify({'error': 'Invalid input data'}), 400

    analysis_id = str(uuid.uuid4())
    socketio.emit('task_status', {'analysis_id': analysis_id, 'status': "Analysis started"}, broadcast=True)
    threading.Thread(target=run_pipeline, args=(mutant_sequence, wild_sequence, analysis_id)).start()
    print("response?")
    return jsonify({"analysis_id": analysis_id}), 200

@app.route('/api/results/pair/<analysis_id>', methods=['GET'])
def get_combined_text(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)

    if not os.path.exists(pipeline_dir):
        return jsonify({'error': 'Analysis not found'}), 404


    #tutaj odczyt odpowiednich danych z bazy danych

    filenames = [
        'RNApdist-result.txt',
        'RNAdistance-result.txt',
        'RNAdistance-backtrack.txt'
    ]

    combined_content = ""
    for filename in filenames:
        file_path = os.path.join(pipeline_dir, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                combined_content += f"=== {filename} ===\n{file.read()}\n\n"
        else:
            combined_content += f"=== {filename} ===\nFile not found\n\n"

    return jsonify({'content': combined_content})

@app.route('/api/results/pair/<analysis_id>/rna-plot-mut', methods=['GET'])
def get_svg_mut(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)
    svg_path = os.path.join(pipeline_dir, 'mut-dotbracket.svg')

    if not os.path.exists(svg_path):
        return jsonify({'error': 'SVG file not found'}), 404

    return send_file(svg_path, mimetype='image/svg+xml')

@app.route('/api/results/pair/<analysis_id>/rna-plot-wt', methods=['GET'])
def get_svg_wt(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)
    svg_path = os.path.join(pipeline_dir, 'wt-dotbracket.svg')

    if not os.path.exists(svg_path):
        return jsonify({'error': 'SVG file not found'}), 404

    return send_file(svg_path, mimetype='image/svg+xml')

@app.route('/api/results/pair/<analysis_id>/hit-tree_wt', methods=['GET'])
def get_svg_hit_tree_wt(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)
    svg_path = os.path.join(pipeline_dir, 'tree_wt.svg')

    if not os.path.exists(svg_path):
        return jsonify({'error': 'SVG file not found'}), 404

    return send_file(svg_path, mimetype='image/svg+xml')

@app.route('/api/results/pair/<analysis_id>/hit-tree_mut', methods=['GET'])
def get_svg_hit_tree_mut(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)
    svg_path = os.path.join(pipeline_dir, 'tree_mut.svg')

    if not os.path.exists(svg_path):
        return jsonify({'error': 'SVG file not found'}), 404

    return send_file(svg_path, mimetype='image/svg+xml')



@app.route('/api/analyze/single', methods=['POST'])
def analyze_single():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    
    wild_sequence = data.get('wildSequence')
    logger.debug(f"Wild sequence: {wild_sequence}")
    
    if not wild_sequence:
        return jsonify({'error': 'Invalid input data'}), 400

    analysis_id = str(uuid.uuid4())

    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)

    os.makedirs(pipeline_dir, exist_ok=True)
    wt_file_path = os.path.join(pipeline_dir, 'wt.txt')

    with open(wt_file_path, 'w') as wt_file:
        wt_file.write(wild_sequence + '\n')

    socketio.emit('task_status', {'analysis_id': analysis_id, 'status': "Analysis started"}, broadcast=True)
    try:
        result = subprocess.run(
            ['python3', os.path.join(BASE_DIR, 'pipeline', 'script.py'), pipeline_dir],
            check=True,
            capture_output=True,
            text=True
        )
        output = result.stdout
        logger.debug(f"Script output: {output}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error while running script: {e.stderr}")
        return jsonify({'error': 'Analysis failed'}), 500
    socketio.emit('task_status', {'analysis_id': analysis_id, 'status': "Analysis completed"}, broadcast=True)

    
    
    logger.debug(f"Response ?: {analysis_id}")
    return jsonify({"analysis_id": analysis_id}), 200

@app.route('/api/results/single/<analysis_id>', methods=['GET'])
def get_csv_preview(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)
    csv_file_path = os.path.join(pipeline_dir, 'mutation_results.csv')
    logger.debug(f"Expected CSV file path: {csv_file_path}")
    
    if not os.path.exists(csv_file_path):
        logger.debug("CSV not found")
        return jsonify({'error': 'File not found'}), 404

    try:
        with open(csv_file_path, 'r') as file:
            lines = file.readlines()
            first_five_lines = ''.join(lines[:5])  
        logger.debug(f"Preview of first five lines: {first_five_lines}")
        return jsonify({'content': first_five_lines})

    #Pewnie tutaj zapis do bazy danych, powyciągać 10 pierwszych danych z .csv

    except Exception as e:
        return jsonify({'error': f'Error reading the file: {str(e)}'}), 500

@app.route('/api/results/<analysis_id>/zip-download', methods=['GET'])
def download_results_zip(analysis_id):
    pipeline_dir = os.path.join(BASE_DIR, 'pipeline', analysis_id)
    zip_path = os.path.join(pipeline_dir, f"{analysis_id}.zip")

    if not os.path.exists(pipeline_dir):
        return jsonify({'error': 'Analysis not found'}), 404

    shutil.make_archive(zip_path.replace(".zip", ""), 'zip', pipeline_dir)
    return send_file(zip_path, as_attachment=True)

@socketio.on('connect')
def handle_connect():
    logger.debug("Backend sent connect")
    emit('response', {'data': 'Connected to WebSocket'})

if __name__ == '__main__':
    eventlet.monkey_patch()
    socketio.run(app, host='0.0.0.0', port=8080)
