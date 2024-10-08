FROM python:3.9 AS backend

WORKDIR /usr/src/backend

COPY . .

WORKDIR /usr/src/backend/pipeline

# Zainstaluj wszystkie niezbędne zależności
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
    liblapack3 \
    libgsl-dev \
    libmpfr-dev \
    && rm -rf /var/lib/apt/lists/*



RUN dpkg --force-depends -i python3-rna_2.6.4-1_amd64.deb || apt-get install -f -y && \
    dpkg --force-depends -i viennarna-dev_2.6.4-1_amd64.deb || apt-get install -f -y && \
    dpkg --force-depends -i viennarna_2.6.4-1_amd64.deb || apt-get install -f -y


WORKDIR /usr/src/backend

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod -R 777 pipeline && ls -ld pipeline

EXPOSE 8080

CMD ["python", "app.py"]
