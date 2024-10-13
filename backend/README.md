##Wlaczenie kontenera osobno
#docker build -t inzynierka .
#docker run -it inzynierka /bin/bash
#wlaczenie z dostepnym portem 8080
#docker run -it -p 8080:8080 inzynierka /bin/bash


docker run -it -p 8080:8080 snp-app-backend /bin/bash