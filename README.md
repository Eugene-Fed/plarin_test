## plarin_test
### Перед запуском
Необходимо установить 3 переменные среды любым из известных способов:  
CLIENT_URI  
DB_NAME  
COLLECTION_NAME  

Наиболее простой способ - добавить в корень проекта файл с именем `.env`, который содержит строки:  
`  
CLIENT_URI='mongodb://localhost:27017/'  
DB_NAME='My_DB'  
COLLECTION_NAME='Employees'
`  
или перечислить переменные в командной строке перед запуском веб-приложения  
`CLIENT_URI="mongodb://localhost:27017/" DB_NAME="My_DB" COLLECTION_NAME="Employees" uvicorn main:app --reload`  
