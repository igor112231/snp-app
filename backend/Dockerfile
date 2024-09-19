FROM python:3.9 AS backend

WORKDIR /usr/src/backend

RUN pip install Flask
RUN pip install mysql-connector-python

# Kopiujemy kod źródłowy
COPY . .

# Ustawiamy port na 8080
EXPOSE 8080

# CMD uruchamia aplikację, gdy kontener jest uruchamiany
CMD ["python", "app.py"]