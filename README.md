## plarin_test

### Перед запуском
Необходимо установить 3 переменные среды любым удобным способом:  
`CLIENT_URI`  
`DB_NAME`  
`COLLECTION_NAME`  

Наиболее простой способ - добавить в корень проекта файл с именем `.env`, который содержит строки:  
```  
CLIENT_URI='mongodb://127.0.0.1:27017/'  
DB_NAME='db_name'  
COLLECTION_NAME='collection_name'
```  
Или задать переменные в командной строке при запуске сервера:  
`CLIENT_URI="mongodb://localhost:27017/" DB_NAME="db_name" COLLECTION_NAME="collection_name" uvicorn main:app --reload`  

### Запуск из консоли
```
pip3 install -r requirements.txt
uvicorn main:app --reload
```

### Запуск из `Docker`:
Предварительно необходимо указать переменные окружения в файл `docker/_env` - он и будет использован для создания файла `.env`.
```
docker build -t plarin_test:tag .
docker run -d --name plarin_test -d plarin_test:tag
```  
При необходимости - указать сопоставление портов `-p 8081:8000`, где `8000` - порт к которому подключается *uvicorn* внутри контейнера, а `8081` - потенциально не занятый порт системы.  
`docker run -d -p 8081:8000 --name plarin_test -d plarin_test:tag`

## TODO
- [x] Добавить фильтр по числовым диапазонам (*Возраст*, *Зарплата*)
- [x] Добавить фильтр по строковым значениям (*Пол*, *Должность*, *Компания*)
- [x] Добавить фильтр по *Дате* устройства на работу (`Позже чем` / `Раньше чем`).
- [x] Наполнить проект тестами  
- [x] ~~Выяснить стандарты в команде: какой из методов `GET` или `POST` используется для получения данных. Во втором случае можно описать тело запроса через класс `SearchModel(BaseModel)`.~~ РЕАЛИЗОВАЛ ОБА МЕТОДА.  
- [x] В коде описан класс обработки подключений к БД. Вместо него в текущей реализации используются **глобальные переменные**. По возможности необходимо упаковать подключение к базе и работу с ней в соответствующий объект.  
- [ ] Решить проблему с автотестами асинхронных функций. Примеры из документации (https://fastapi.tiangolo.com/ru/tutorial/testing/) работают до тех пор, пока методы подключения к БД нахоятся в коде `main.py`, а также пока используются глобальные переменные. При выносе методов подключения к БД в отдельный модуль, начинает сыпаться ошибка: `RuntimeError: Event loop is closed` на всех тестах, кроме первого запущенного. Причем 'проходит' всегда ТОЛЬКО первый тест, какой бы из них ни был поставлен на первое место в очереди. Остальные - падают.  
- [ ] Добавить фильтры по спискам значений (*Пол*, *Должность*, *Компания*). Списки значений могут быть переданы как повторяющийся ключ с разными значениями:  
`?company=Yandex&company=Google&company=Plarin`  
- [ ] Добавить аутентификацию.

## TUTORIALS
https://github.com/tiangolo/fastapi/issues/50 - Способ передачи списка значений в параметр запроса.  
https://tsmx.net/docker-local-mongodb/ - Подключение Докер-контейнера к локально запущенной MongoDB.  
https://www.ibm.com/docs/ru/urbancode-build/6.1.2?topic=reference-rest-api-conventions - Соглашение для `API REST`, в т.ч. о правилах работы с сортировкой (в конце документа).  
https://metanit.com/nosql/mongodb/2.7.php - Альтернативный способ ограничить выборку по значению поля (подходит для полей *Возраст* и *Зарплата*).  
https://fastapi.tiangolo.com/ru/tutorial/testing/ - Автотесты.  
https://fastapi.tiangolo.com/tutorial/body/ - Pydantic Модель для офрмления Тела POST запросов.  
https://fastapi.tiangolo.com/tutorial/response-model/ - Pydantic Модель для офрмления Ответа.  
https://www.mongodb.com/docs/compass/current/query/filter/ - Шпаргалка по работе с `MongoDB`.  
https://motor.readthedocs.io/en/stable/api-asyncio/asyncio_motor_collection.html#motor.motor_asyncio.AsyncIOMotorCollection.find - Шпаргалка по работе с `Motor`.  
https://github.com/tiangolo/fastapi/issues/2003#issuecomment-909379022 - Решение для асинхронных тестов FastAPI в фиде фабрики создания и закрытия "аппов" для каждого теста.  
