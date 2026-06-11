# Ponto de entrada para rodar a dashboard via terminal:
#   python run.py
# Equivalente a: streamlit run app.py

import subprocess
import sys
import os

if __name__ == "__main__":
    try:
        import streamlit
    except ImportError:
        print("Streamlit nao instalado. Execute: pip install -r requirements.txt")
        sys.exit(1)

    dashboard = os.path.join(os.path.dirname(__file__), "app.py")
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard])
