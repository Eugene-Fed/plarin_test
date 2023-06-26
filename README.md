## plarin_test
### Перед запуском
Необходимо установить 3 переменные среды любым удобным способом:  
`CLIENT_URI`  
`DB_NAME`  
`COLLECTION_NAME`  

Наиболее простой способ - добавить в корень проекта файл с именем `.env`, который содержит строки:  
```  
CLIENT_URI='mongodb://localhost:27017/'  
DB_NAME='My_DB'  
COLLECTION_NAME='Employees'
```  
или задать переменные в командной строке при запуске сервера  
`CLIENT_URI="mongodb://localhost:27017/" DB_NAME="My_DB" COLLECTION_NAME="Employees" uvicorn main:app --reload`  

### Запуск
Команда `uvicorn main:app --reload` (при условии предварительно заданных переменных окружения).  

## TODO
- [x] Добавить фильтр по *Дате* устройства на работу.
- [ ] Добавить фильтры по спискам значений (*Пол*, *Должность*, *Компания*).
- [ ] Выяснить стандарты в команде: какой из методов `GET` или `POST` используется для получения данных.
- [ ] В коде описан класс обработки подключений к БД. Вместо него в текущей реализации используются **глобальные переменные**. По возможности необходимо упаковать подключение к базе и работу с ней в соответствующий объект.
- [ ] Добавить аутентификацию.
