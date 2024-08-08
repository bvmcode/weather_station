FROM python:3.10-slim

COPY ./requirements.txt /data/requirements.txt

WORKDIR /data

RUN python -m pip install -r requirements.txt

COPY . /data

CMD ["python", "-u", "etl.py"]