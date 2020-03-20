FROM python:3.8-slim-buster

RUN apt-get update \
 && apt-get install --no-install-recommends -y \
    ca-certificates \
    curl \
    build-essential \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN ls -al

RUN pip install -r /app/requirements.txt \
 && rm -f /app/requirements.txt

WORKDIR /app/src

ENV PORT 8501

EXPOSE ${PORT}

CMD ["/app/entrypoint.sh"]
