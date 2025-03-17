# Basis-Image mit Python 3.11
FROM python:3.11

WORKDIR /app

RUN python -m venv /app/venv 

# Dependencies installieren (wird gecached)
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PATH="/app/venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

