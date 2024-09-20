import uuid
from flask import Flask, jsonify, request
from flasgger import Swagger
import mysql.connector
import os

app = Flask(__name__)
swagger = Swagger(app, template_file='openapi.yml')  # Ładowanie zewnętrznego pliku YAML


# Konfiguracja połączenia z bazą danych
db_config = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'qwas'),
    'database': os.getenv('MYSQL_DATABASE', 'snp')
}


# Przykładowe dane w pamięci (możesz to zamienić na bazę danych)
tasks = {}

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Analysis Results API!"}), 200

#Jeszcze trzeba zmienić id z inta na format UUID w bazie danych !
# Funkcja do uzyskania połączenia z bazą danych
def connect_to_database():
    return mysql.connector.connect(**db_config)

@app.route('/api/analyze', methods=['POST'])
def submit_analysis():
    data = request.json
    sequence_wt = data.get('sequence_wt')
    sequence_mt = data.get('sequence_mt')

    if not sequence_wt or not sequence_mt:
        return jsonify({"error": "Invalid input format"}), 400

    # Generowanie unikalnego identyfikatora
    task_id = str(uuid.uuid4())

    # Połączenie z bazą danych
    conn = connect_to_database()
    cursor = conn.cursor()
    #Tu jeszcze można dodać status jako pole w bazie danych 
    cursor.execute(
    "INSERT INTO analysis_results (id, normalSequence, wildSequence) VALUES (%s, %s, %s)",
    (task_id, sequence_mt, sequence_wt)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"id": task_id}), 200

@app.route('/api/status/<string:id>', methods=['GET'])
def check_status(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT status FROM analysis_results WHERE id = %s", (id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()

    if task is None:
        return jsonify({"error": "Invalid task id"}), 404

    return jsonify({"status": task['status'], "reason": None}), 200

@app.route('/api/result/<string:id>', methods=['GET'])
def get_result(id):
    conn = connect_to_database()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT result FROM analysis_results WHERE id = %s", (id,))
    task = cursor.fetchone()
    cursor.close()
    conn.close()

    if task is None:
        return jsonify({"error": "Invalid task id"}), 404

    if task['status'] != "DONE":
        return jsonify({"error": "Task is not completed yet"}), 404

    return jsonify(task['result']), 200

#==========================================================================================================================
# Funkcja do uzyskania połączenia z bazą danych
def connect_to_database():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Test polaczenia
@app.route('/test-db')
def test_db():
    conn = connect_to_database()
    if conn is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify(result)

# Dodawania wyniku analizy (POST)
@app.route('/analysis-results', methods=['POST'])
def add_analysis_result():
    data = request.json
    normal_sequence = data.get('normalSequence')
    wild_sequence = data.get('wildSequence')
    result = data.get('result')

    conn = connect_to_database()
    if conn is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO analysis_results (normalSequence, wildSequence, result) VALUES (%s, %s, %s)",
        (normal_sequence, wild_sequence, result)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Result added successfully!"}), 201

# Wyświetlanie wszystkich wyników analizy (GET)
@app.route('/analysis-results', methods=['GET'])
def get_analysis_results():
    conn = connect_to_database()
    if conn is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM analysis_results")
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)

# Dodawanie wyniku analizy (GET z parametrami)
@app.route('/add-analysis-result', methods=['GET'])
def add_analysis_result_get():
    normal_sequence = request.args.get('normalSequence')
    wild_sequence = request.args.get('wildSequence')
    result = request.args.get('result')

    if not normal_sequence or not wild_sequence or not result:
        return jsonify({"error": "Missing parameters"}), 400

    conn = connect_to_database()
    if conn is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO analysis_results (normalSequence, wildSequence, result) VALUES (%s, %s, %s)",
        (normal_sequence, wild_sequence, result)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Result added successfully!"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)