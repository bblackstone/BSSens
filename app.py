import os
import sqlite3
import datetime
import smtplib
from flask import Flask, jsonify, send_file
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd

app = Flask(__name__)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'your_email@gmail.com'
SMTP_PASSWORD = 'your_password'  # Or use an App Password if 2-Step Verification is enabled
EMAIL_FROM = 'elme@gmail.com'
EMAIL_TO = 'recipient_email@example.com'
EMAIL_SUBJECT = 'Sensor Alert'

# Define database setup
def create_db():
    conn = sqlite3.connect('sensor_data.db')
    con = conn.cursor()
    con.execute('''CREATE TABLE IF NOT EXISTS sensor_data
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                temperature REAL,
                humidity REAL,
                timestamp TEXT)
                ''')

    # Insert fake data
    fake_data = [
        (22.5, 45.0, '2023-10-01 10:00:00'),
        (23.0, 50.0, '2023-10-01 11:00:00'),
        (83.0, 50.0, '2023-10-01 11:00:00'),
        (21.5, 55.0, '2023-10-01 12:00:00')
    ]
    con.executemany("INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)", fake_data)

    conn.commit()
    conn.close()

# Function to insert data into the database
def insert_data(temperature, humidity):
    conn = sqlite3.connect('sensor_data.db')
    con = conn.cursor()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    con.execute("INSERT INTO sensor_data (temperature, humidity, timestamp) VALUES (?, ?, ?)",
              (temperature, humidity, timestamp))
    
    conn.commit()
    conn.close()

    
# Flask route to fetch DHT11 sensor data and store in database
@app.route('/data', methods=['GET'])
def get_data():
    if os.name == 'nt':  # Check if the OS is Windows
        # Return mock data for development on Windows
        humidity, temperature = 50.0, 22.0
    else:
        import Adafruit_DHT
        sensor = Adafruit_DHT.DHT11
        pin = 4 # Port in the Ruspberry PI3 which is connected with the sensor DHT11
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)

    if humidity is not None and temperature is not None:
        insert_data(temperature, humidity)
        
        return jsonify({
            'temperature': temperature,
            'humidity': humidity,
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({'error': 'Failed to get reading from the sensor'}), 500

# Flask route to generate report
@app.route('/report', methods=['GET'])
def generate_report():
    conn = sqlite3.connect('sensor_data.db')
    df = pd.read_sql_query("SELECT * FROM sensor_data", conn)
    conn.close()

    # Save the dataframe to CSV and Excel
    csv_path = 'sensor_report.csv'
    excel_path = 'sensor_report.xlsx'
    df.to_csv(csv_path, index=False)
    df.to_excel(excel_path, index=False)

    return jsonify({'message': 'Reports generated successfully'})

# Flask route to download CSV report
@app.route('/download/sensor_report.csv', methods=['GET'])
def download_csv():
    return send_file('sensor_report.csv', as_attachment=True)

# Flask route to download Excel report
@app.route('/download/sensor_report.xlsx', methods=['GET'])
def download_excel():
    return send_file('sensor_report.xlsx', as_attachment=True)

if __name__ == '__main__':
    create_db()
    app.run(debug=True)