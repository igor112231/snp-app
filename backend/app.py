from flask import Flask, jsonify, request
import mysql.connector
import os
import threading
import time
import subprocess
import tempfile

app = Flask(__name__)

# Konfiguracja połączenia z bazą danych
db_config = {
    'host': os.getenv('MYSQL_HOST', 'mysql'),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'qwas'),
    'database': os.getenv('MYSQL_DATABASE', 'snp')
}


# Funkcja do uzyskania połączenia z bazą danych
def connect_to_database():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def rna_pdist_run(sequence1, sequence2):
    # Utworzenie pliku tymczasowego do zapisu sekwencji
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write(f"{sequence1}\n{sequence2}")
        temp_filename = temp_file.name

    # Uruchomienie polecenia RNApdist na pliku tymczasowym
    command = f"RNApdist < {temp_filename}"

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Sprawdzanie, czy polecenie zakończyło się pomyślnie
    if result.returncode == 0:
        # Zapisz wynik do zmiennej
        output = result.stdout.strip()  # Usuwa dodatkowe białe znaki
        print("Wynik RNApdist:")
        print(output)
    else:
        print("Wystąpił błąd podczas uruchamiania RNApdist:")
        print(result.stderr)

    # Usunięcie pliku tymczasowego
    os.remove(temp_filename)

#http://127.0.0.1:8080/rna-pdist?sequence1=ACGUACGU&sequence2=UGCAUGCA
@app.route('/rna-pdist', methods=['GET'])
def rna_pdist():
    # Pobierz sekwencje z parametrów zapytania
    sequence1 = request.args.get('sequence1')
    sequence2 = request.args.get('sequence2')

    if not sequence1 or not sequence2:
        return jsonify({"error": "Brak sekwencji RNA w żądaniu"}), 400

    # Uruchomienie funkcji w osobnym wątku
    thread = threading.Thread(target=rna_pdist_run, args=(sequence1, sequence2))
    thread.start()
    
    return jsonify({"message": "Zadanie rozpoczete!"}), 202


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