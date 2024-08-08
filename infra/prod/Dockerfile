FROM python:3.10-slim

COPY ./requirements.txt /data/requirements.txt
COPY ./.env /data/.env
COPY ./etl.py /data/etl.py

WORKDIR /data

RUN python -m pip install -r requirements.txt

CMD ["python", "-u", "etl.py"]