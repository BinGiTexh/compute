FROM arm64v8/python:3.9-slim

WORKDIR /app

RUN pip install --no-cache-dir requests docker

COPY monitor.py /app/

CMD ["python", "-u", "monitor.py"]
