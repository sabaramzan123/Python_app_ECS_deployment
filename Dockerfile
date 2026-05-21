# Python ka official image use karein
FROM python:3.9-slim

# Working directory set karein
WORKDIR /app

# Requirements copy karein aur install karein
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baaki saari code files copy karein
COPY . .

# Streamlit ka default port expose karein
EXPOSE 8501

# App run karne ke liye command
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]