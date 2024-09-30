FROM node:21.6.1
WORKDIR /usr/src/app

COPY package*.json ./

RUN npm install
RUN npm install socket.io-client@3


COPY . .

RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "start"]