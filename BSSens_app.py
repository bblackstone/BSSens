import streamlit as st
import requests
import pandas as pd

FLASK_API_URL = ''

# Streamlit Interface
st.title('BSSens Dashboard')

# Button to fetch the latest data from the Flask API
if st.button('Get Data'):
    try:
        response = requests.get(f'{FLASK_API_URL}/data')
        data = response.json()

        if 'error' in data:
            st.error('Failed to retrieve data from the sensor')
        else:
            st.success('Data retrieved successfully!')
            st.write(f"Temperature: {data['temperature']}°C")
            st.write(f"Humidity: {data['humidity']}%")
            st.write(f"Timestamp:{data['timestamp']}")
    except requests.exception.RequestException as e:
        st.error(f"Error: {e}")

# Button to generate report (CSV and Excel)
# Button pour generer les rapports
if st.button('Generate Report'):
    try:
        response = requests.get(f'{FLASK_API_URL}/report')
        data = response.json()

        if 'message' in data:
            st.success(data['message'])
            st.write("Download the generated reports:")
            st.markdown(f"[Download CSV Report](http://{FLASK_API_URL}/download/sensor_report.csv)")
            st.markdown(f"[Download Excel Report](http://{FLASK_API_URL}/download/sensor_report.xlsx)")
        else:
            st.error('Failed to generate the report')
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")

# Display the data from the database
# Consulter les donnee situer dans la base de donnee
if st.button('View Data From Database'):
    try:
        response = requests.get(f'{FLASK_API_URL}/data')
        data = response.json()

        if 'error' in data:
            st.error('Failed to retrieve data from the sensor')
        else:
            # Display historical sensor data from the DHT11
            # L'Affichage des donnee historique capter par DHT11#
            conn = sqlite3.connect('sensor_data.db')
            df = pd.read_sql_query("SELECT * FROM sensor_data", conn)
            conn.close()
            # Display the table
            # Affichage de la table
            st.write(df)
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")