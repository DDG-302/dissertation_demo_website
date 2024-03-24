# app/Dockerfile

FROM python:3.10-slim-bullseye

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

ADD main.py . 
ADD dialogue.py . 
ADD data /app/data 
ADD assets /app/assets
ADD requirements.txt .
ADD utils /app/utils

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "main.py"]