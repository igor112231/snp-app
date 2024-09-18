// Importujemy bibliotekę Express
const express = require('express');

// Tworzymy instancję aplikacji Express
const app = express();

// Ustawiamy port na 3000
const PORT = 3001;

// Definiujemy prostą trasę, która odpowiada na zapytanie GET na ścieżce "/"
app.get('/', (req, res) => {
  res.send('Hello, World!');
});

// Uruchamiamy serwer
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
