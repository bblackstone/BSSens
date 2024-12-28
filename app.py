from flak import Flask, jsonify
import Adafruit_DHT
import sqlite3
import datetime
import pandas as pd
import os
app = Flask(__name__)

# Define database setup
# Definition de la base de donnee

def create_db():
    conn = sqlite3.connect('sensor_data.db')
    con = conn.cursor()
    con.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                humidity REAL,
                timestamp TEXT)
                ''')

    conn.commit()
    conn.close

# Function to insert data into the database
# L'insertion dans la base de donnee

def insert_data(temperature, humidity):
    conn = sqlite3.connect('sensor_data.db')
    con = conn.cursor()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    con.execute("INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)",
              (temperature, humidity, timestamp))
    
    conn.commit()
    conn.close()

# Flask route to fetch DHT11 sensor data and store in database
# Flask routage pour l'extraction des donnees du DHT11
@app.route('/data', methods=['GET'])
def get_data():
    sensor = Adafruit_DHT.DHT11
    pin = 4 # port de la connection avec Raspberry PI3
    humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and temperature is not None:
        insert_data(temperature, humidity)
        return jsonify({
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

    else:
        return jsonify({'error': "Failed to retrieve data | Echec de l'extraction des donnees"}), 500
    
# Endpoint to generate reports (Excel & CSV)
# End-Point pour generer les raports sous les formes d'excel et csv
 @app.route('/report', methods=['GET'])
def generate_report():
    conn = sqlite3.connect('sensor_data.db')
    df = pd.read_sql_query("SELECT * FROM sensor_data", conn)
    conn.close()

    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    
    csv_path = 'reports/sensor_report.csv',
    excel_path = 'reports/sensor_report.xlsx'

    # CSV Report
    # CSV Rapport
    df.to_csv(csv_path, index=False)

    # Excel Report
    # Excel Rapport
    df.to_excel(excel_path, index=False)

    return jsonify({
        'message': 'Report generated successfully!',
        'csv_download_link': f'/download/{os.path.basename(csv_path)}',
        'excel_download_link': f'/download/{os.path.basename(excel_path)}'
    })


# Download Reports
# Telechargement des rapports
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory('reports', filename)


if __name__ == '__main__':
    create_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
    