FROM python:3.6

RUN mkdir /home/www-data && mkdir /home/www-data/app \
    && mkdir /home/www-data/app/src \
    && mkdir /home/www-data/app/app \
    && mkdir /home/www-data/app/kaira

WORKDIR /home/www-data/app/src/

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#COPY server.py /usr/src/app/src

VOLUME ["/home/www-data/app/src/",\
        "/home/www-data/app/kaira/"]

CMD [ "gunicorn", "-w", "2", "--bind", "0.0.0.0:8000", "--worker-class", "meinheld.gmeinheld.MeinheldWorker", "server:app"]
