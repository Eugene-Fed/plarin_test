## plarin_test
### Перед запуском
Необходимо установить 3 переменные среды любым из известных способов:  
CLIENT_URI  
DB_NAME  
COLLECTION_NAME  

Наиболее простой способ добавить их в файл с именем `.env` в корне проекта вида:  
`  
CLIENT_URI=mongodb://localhost:27017/  
DB_NAME="My_DB"  
COLLECTION_NAME="Employees"
`  
или указать их в командной строке перед запуском веб-приложения  
`CLIENT_URI="mongodb://localhost:27017/" DB_NAME="My_DB" COLLECTION_NAME="Employees" uvicorn main:app --reload`  
