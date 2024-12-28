import os
import subprocess
import platform
import threading

def run_flask():
    if platform.system() == "Windows":
        subprocess.run("python app.py", shell=True)
    else:
        subprocess.run("python3 app.py", shell=True)

def run_streamlit():
    subprocess.run("streamlit run BSSens_app.py", shell=True)

def run_requirements():
    subprocess.run("pip install -r requirements.txt", shell=True)

def main():
    # Create threads for Flask and Streamlit
    run_requirements()
    flask_thread = threading.Thread(target=run_flask)
    streamlit_thread = threading.Thread(target=run_streamlit)

    # Start the threads
    flask_thread.start()
    streamlit_thread.start()

    # Wait for both threads to complete
    flask_thread.join()
    streamlit_thread.join()

if __name__ == "__main__":
    main()