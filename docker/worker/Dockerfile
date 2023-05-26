FROM python:3.11.3-alpine3.18

WORKDIR /usr/src/app
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . .

ENV PYTHONPATH "/usr/src/app"

COPY ./docker/worker/entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

CMD ["python", "./worker.py"]
