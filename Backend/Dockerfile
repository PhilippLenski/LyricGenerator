# Basis-Image mit Python 3.11
FROM python:3.11

# Setze Arbeitsverzeichnis
WORKDIR /app

# Installiere System-Abhängigkeiten für Hugging Face Model-Download
RUN apt-get update && apt-get install -y git wget unzip && \
    rm -rf /var/lib/apt/lists/*

# Installiere Hugging Face Hub CLI
RUN pip install --no-cache-dir huggingface_hub

# 📌 Setze den Hugging Face API-Token (MUSS MANUELL EINGETRAGEN WERDEN!)
ARG HF_TOKEN="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"
ENV HF_HOME="/app/models"
RUN huggingface-cli login --token $HF_TOKEN

# 📌 Modell automatisch von Hugging Face herunterladen
RUN mkdir -p /app/models && \
    python -c "from huggingface_hub import snapshot_download; \
               snapshot_download(repo_id='google/gemma-3-4b-it', cache_dir='/app/models')"

# Kopiere nur requirements.txt zuerst, um Cache zu nutzen
COPY requirements.txt .

# Installiere Python-Abhängigkeiten
RUN pip install --no-cache-dir -r requirements.txt

# Kopiere restliche Dateien ins Arbeitsverzeichnis
COPY . .

# Exponiere Port für FastAPI
EXPOSE 8000

# Starte FastAPI-Server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

