FROM apache/airflow:3.1.0

USER airflow

RUN pip install --no-cache-dir \
    "psycopg[binary]==3.3.5" \
    "pandas==3.0.5" \
    "python-dotenv==1.2.3" \
    "requests==2.34.2" \
    "gtfs-realtime-bindings==3.0.0" \
    "protobuf==7.36.2"
