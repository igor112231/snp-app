FROM python:3.9 AS backend

# Ustawiamy katalog roboczy
WORKDIR /usr/src/backend

# Instalujemy narzędzia do kompilacji oraz zależności
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    cmake \
    git \
    libboost-all-dev \
    && rm -rf /var/lib/apt/lists/*

# Pobierz ViennaRNA
RUN wget https://www.tbi.univie.ac.at/RNA/download/sourcecode/2_6_x/ViennaRNA-2.6.4.tar.gz \
    && tar -zxvf ViennaRNA-2.6.4.tar.gz

# Kompilacja ViennaRNA
WORKDIR /usr/src/backend/ViennaRNA-2.6.4
RUN ./configure --prefix=/usr/local

# Kompilacja z pojedynczym wątkiem i debugowaniem
RUN make -j1 V=1 || true
RUN make install || true

# Instalujemy Flask i inne zależności Python
RUN pip install Flask mysql-connector-python

# Kopiujemy kod źródłowy
COPY . .

# Instalujemy zależności z pliku requirements.txt
RUN pip install -r requirements.txt

# Ustawiamy port na 8080
EXPOSE 8080

CMD ["python", "app.py"]
