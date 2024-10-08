FROM python AS backend

WORKDIR /usr/src/backend


COPY . .

WORKDIR /usr/src/backend/pipeline


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
    && rm -rf /var/lib/apt/lists/*

# --force depends
RUN apt-get update && apt-get install -y \
    && dpkg -i ./python3-rna_2.6.4-1_amd64.deb && \
    dpkg -i ./viennarna-dev_2.6.4-1_amd64.deb && \
    dpkg -i ./viennarna_2.6.4-1_amd64.deb || true && \
    apt-get install -f -y && \
    rm -rf /var/lib/apt/lists/*


WORKDIR /usr/src/backend


RUN pip install --no-cache-dir -r requirements.txt


RUN chmod -R 777 pipeline && ls -ld pipeline

EXPOSE 8080


CMD ["python", "app.py"]