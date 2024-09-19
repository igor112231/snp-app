# snp-app

## Włączenie aplikacji

```
docker-compose up --build

```

## Baza danych

```
http://localhost:8081

```

## Backend

```
http://localhost:8080

```

# Test polaczenia z baza danych

```
http://127.0.0.1:8080/test-db

```

# Test dodania wiersza (zamiast get powinno sie uzywac post ale jeszcze nie ma frontendu)

```
http://localhost:8080/add-analysis-result?normalSequence=AGTC&wildSequence=TGCA&result=positive%22

```

# Test wyswietlania elementow z bazy danych

```
http://localhost:8080/analysis-results

```

## Frontend

```
http://localhost:3000

```
