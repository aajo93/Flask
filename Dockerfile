FROM python:3.9.16

RUN apt-get update && \
    #apt-get install -y postgresql-client-13 && \
    apt-get install -y default-libmysqlclient-dev 

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app app
COPY application.py .

EXPOSE 5000

CMD [ "python", "application.py"]