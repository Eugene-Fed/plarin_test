from fastapi import FastAPI, Request
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel

app = FastAPI()
# TODO - вынести эти параметры в файл настроек/.env/PATH
CLIENT_URI = r'mongodb://localhost:27017/'
DB_NAME = r'plarin_test'
COLLECTION_NAME = r'employees_test'

QUERY = {'company': 'Yandex'}

# TODO - заменить использование глобальных переменных на классы `ConnetcionToDB` и `Collection`.
_client = None
_db = None
_collection = None


class ConnectionToDB:
    # TODO - Создать объект подключения к БД

    def __init__(self):
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
        self.collection: AsyncIOMotorCollection = None

    async def get_db_connection(self, client_uri: str) -> AsyncIOMotorClient:
        self.client = await AsyncIOMotorClient(client_uri)


class Collection(ConnectionToDB):
    # TODO - Создать объект Коллекции БД
    pass


# TODO - Сделать эту функцию методом класса `ConnectionToDB`
def connect_to_db(client_uri=CLIENT_URI, db_name=DB_NAME, collection_name=COLLECTION_NAME):
    """
    Подключение к заданное коллекции БД
    :param client_uri:
    :param db_name:
    :param collection_name:
    :return:
    """
    global _client
    global _db
    global _collection
    try:
        _client = motor.motor_asyncio.AsyncIOMotorClient(client_uri)
        _db = _client[db_name]
        _collection = _db[collection_name]
        print('Server connection was opened')
    except ServerSelectionTimeoutError:
        print('Server connection TimeoutError')
    except Exception as e:
        print(e)


# TODO - Сделать эту функцию методом класса `ConnectionToDB`
def disconnect_from_db(client=_client):
    if client is not None:
        try:
            client.close()
            print('Server connection was closed')
        except Exception as e:
            print(e)


@app.on_event("startup")
async def startup():
    connect_to_db()
    # TODO - при замене Глобала на классы подключений
    # app.state.db = ConnectionToDB(params)


@app.on_event("shutdown")
async def shutdown():
    disconnect_from_db()


@app.get('/search/employees')
async def search_employees(company: str, salary: int = None, limit: int = None):
    # TODO - Переписать передачу параметров через класс `pydantic`
    # TODO - Реализовать более сложные фильтры с использованием разных методов `mongodb` вроде `.sort()`, `.limit()`
    query = {'company': company}

    """Вместо того, чтобы убрать лишь столбец `_id`, мы перечисляем все НЕОБХОДИМЫЕ столбцы.
    Это послужит защитой от передачи по ошибке чувствительных данных (номер карты, хеш пароля)."""
    # TODO - реализовать передачу через параметры только необходимых полей БД
    columns = {'_id': 0, 'name': 1, 'email': 1, 'age': 1, 'company': 1, 'join_date': 1, 'job_title': 1,
               'gender': 1, 'salary': 1}
    search_filter = _collection.find(query, columns)
    # TODO - реализовать возможность фильтрации по всем или лишь по некоторым полям на выбор
    if limit:
        search_filter = search_filter.limit(limit)

    employees = []
    try:

        # employees = [employee for employee in await _collection.find({'company': company}, {'_id': 0}).to_list(None)]
        employees = [employee for employee in await search_filter.to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        print('Server Selection Timeout Error')
    except Exception as e:
        print(e)
        # todo - return `500`

    return employees
