FROM python:3.8-slim-buster

WORKDIR /flask-docker

RUN python3 -m pip install --upgrade pip

COPY requirements.txt requirements.txt

COPY . .

RUN pip3 install -r requirements.txt

CMD ["streamlit", "run", "app.py", "--server.port=5000", "--server.address=0.0.0.0"]