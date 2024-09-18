# Wskazanie obrazu bazowego
FROM ubuntu:latest

WORKDIR /home/ubuntu

# Uaktualnienie listy pakietów i zainstalowanie zależności
RUN apt-get update && apt-get install -y \
    curl \
    software-properties-common

# Dodanie oficjalnego repozytorium Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_16.x | bash -

# Instalacja Node.js i npm
RUN apt-get install -y nodejs

# Weryfikacja instalacji (opcjonalnie)
RUN node -v && npm -v

# Aktualizacja repozytoriów i instalacja wymaganych pakietów
RUN apt-get update && \
    apt-get install -y \
        software-properties-common \
        build-essential \
        ghostscript \
        texlive \
        pdf2svg \
        texlive-font-utils \
        python3

RUN ln -s /usr/bin/python3 /usr/bin/python

RUN apt-get clean & \
    rm -rf /var/lib/apt/lists/*

RUN npm install -g svgo

# Instalacja ViennaRNA
               
RUN curl -fsSL https://www.tbi.univie.ac.at/RNA/download/sourcecode/2_6_x/ViennaRNA-2.6.4.tar.gz -o ViennaRNA-2.6.4.tar.gz
RUN tar -zxvf ViennaRNA-2.6.4.tar.gz
WORKDIR /home/ubuntu/ViennaRNA-2.6.4
RUN ./configure
RUN make
RUN make install
WORKDIR /home/ubuntu

#RUN curl -fsSL https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tgz -o Python-2.7.9.tgz
#RUN tar xzf Python-2.7.9.tgz
#WORKDIR /home/ubuntu/Python-2.7.9
#RUN ./configure --enable-optimizations
#RUN make altinstall

#RUN ln -sfn '/usr/local/bin/python2.7' '/usr/bin/python'

WORKDIR /home/ubuntu/pipeline
