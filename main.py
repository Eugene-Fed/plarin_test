from fastapi import FastAPI, Request
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import asyncio
import motor.motor_asyncio
from pydantic import BaseModel

app = FastAPI()
# TODO - убрать из харкода. Набор констант для тестов
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
    # _collection: motor.motor_asyncio.AsyncIOMotorCollection = _db[collection_name]
    pass


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


@app.get('/')
async def search_employees(company: str, min_age: int, max_age: int):
    # TODO - Переписать передачу параметров через класс `pydantic`
    # TODO - Реализовать более сложные фильтры с использованием разных методов `mongodb` вроде `.sort()`, `.limit()`

    employees = []
    try:
        '''
        get_filter = find({quert})
        if sort:
            get_filter = get_filter.sort()
        if limit:
            get_filter = get_filter.limit()
        '''

        employees = [employee for employee in await _collection.find({'company': company}, {'_id': 0}).to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        print('Server Selection Timeout Error')
    except Exception as e:
        print(e)
        # todo - return `500`

    return employees
