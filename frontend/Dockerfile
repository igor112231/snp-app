FROM node:21.6.1
WORKDIR /usr/src/app

# Kopiuje pliki package.json oraz package-lock.json (jeśli istnieje)
COPY package*.json ./

# Instalacja zależności
RUN npm install

# Instalacja socket.io-client i typów
RUN npm install socket.io-client@latest
RUN npm install @types/socket.io-client

# Kopiowanie całej aplikacji do kontenera
COPY . .

# Budowanie aplikacji 
RUN npm run build

# Otwiera port 3000
EXPOSE 3000

# Uruchamia aplikację
CMD ["npm", "run", "start"]
