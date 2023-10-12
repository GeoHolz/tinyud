FROM     python:slim
WORKDIR  /app
COPY     ./app.py       ./
COPY     ./wsgi.py      ./
COPY     ./tinyud.py    ./
COPY 	 ./initdb.py 	./
COPY     static ./static
COPY     templates ./templates
COPY    ./requirements.txt              ./
RUN     pip install --upgrade pip --no-cache-dir
RUN     pip install -r ./requirements.txt --no-cache-dir
RUN	    mkdir /app/db
RUN     python3 /app/initdb.py
CMD     ["gunicorn","-w", "1","wsgi:app","--bind", "0.0.0.0:8765"]
