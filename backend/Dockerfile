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
    automake \
    gawk \
    ghostscript \
    texlive \
    pdf2svg \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Pobieramy ViennaRNA
RUN wget https://www.tbi.univie.ac.at/RNA/download/sourcecode/2_6_x/ViennaRNA-2.6.4.tar.gz \
    && tar -zxvf ViennaRNA-2.6.4.tar.gz

# Kompilacja ViennaRNA
WORKDIR /usr/src/backend/ViennaRNA-2.6.4
RUN ./configure --prefix=/usr/local
RUN make -j1 && make install

# Powrót do katalogu roboczego
WORKDIR /usr/src/backend

# Kopiujemy requirements.txt do kontenera
COPY requirements.txt .

# Instalujemy zależności z pliku requirements.txt
RUN pip install -r requirements.txt

# Kopiujemy resztę kodu źródłowego
COPY . .

# Zmieniamy uprawnienia dla plików w pipeline
RUN chmod +x pipeline/*

# Dodajemy ViennaRNA do PATH
ENV PATH="/usr/local/bin:$PATH"

# Otwieramy port 8080
EXPOSE 8080

# Komenda uruchamiająca aplikację
CMD ["python", "app.py"]
