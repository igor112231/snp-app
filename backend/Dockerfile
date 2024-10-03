FROM python:3.9 AS backend

# Instalacja narzędzi systemowych i zależności
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    cmake \
    git \
    ghostscript \
    texlive \
    pdf2svg \
    npm \
    liblapack-dev \
    && rm -rf /var/lib/apt/lists/*

# Kopiuje i instaluje ViennaRNA z pliku .deb
COPY viennarna_2.6.4-1_amd64.deb ./
RUN apt-get update && apt-get install -f -y ./viennarna_2.6.4-1_amd64.deb || true && rm viennarna_2.6.4-1_amd64.deb

# Powrót do katalogu roboczego
WORKDIR /usr/src/backend

# Kopiuje requirements.txt do kontenera
COPY requirements.txt .

# Instalacja zależności z pliku requirements.txt
RUN pip install -r requirements.txt

# Kopiuje reszte kodu źródłowego
COPY . .

# Zmienia uprawnienia dla plików w pipeline
RUN chmod +x pipeline/*

# Otwieramy port 8080
EXPOSE 8080

# Komenda uruchamiająca aplikację
CMD ["python", "app.py"]
