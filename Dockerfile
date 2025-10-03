FROM python:3.12-slim-bookworm
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        python3-dev \
    && rm -rf /var/lib/apt/lists/*


COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt
COPY ./src /src
WORKDIR /src
ENTRYPOINT ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]