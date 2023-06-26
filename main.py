from typing import Annotated
from fastapi import FastAPI, HTTPException, Depends
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection, AsyncIOMotorCursor
from pydantic import BaseModel, BaseSettings, Field
from pathlib import Path
from datetime import datetime

# from pymongo import MongoClient
# import dotenv
# import asyncio


class Settings(BaseSettings):
    """
    Дата класс для получения параметров подключения к ДБ из переменных окружения.
    """
    app_name: str = 'GetEmployees'
    client_uri: str
    db_name: str
    collection_name: str


class SearchModel(BaseModel):
    """
    # TODO - выяснить стандарты команды и при необходимости использовать POST-запросы вместо GET для получения данных
    Модель данных для передачи параметров в виде POST запроса.
    """
    company: str | list[str] | None = Field(default=None)               # Название Компании
    min_age: int | None = Field(default=None, gt=0)                     # Минимальный возраст
    max_age: int | None = Field(default=None, gt=0)                     # Максимальный возраст
    limit: int | None = Field(default=None, gt=0)                       # Лимит количества данных в выдаче
    name: str | None = None
    email: str | None = None                                            # TODO - валидировать формат почты
    join_date: str | datetime | None = None                             # TODO - валидировать формат даты
    job_title: str | list[str] | None = None
    gender: str = Field(default=None, description='One of ["male" | "female" | "other"]')
    min_salary: int | float | None = Field(default=None, gt=0)
    max_salary: int | float | None = Field(default=None, gt=0)
    sort: dict[str, int] | None = None                    # `1` - по возрастанию, `-1` - по убыванию


class ReturnModel(BaseModel):
    name: str
    email: str
    age: int
    company: str
    join_date: str | datetime
    job_title: str
    gender: str = Field(default=None, description='One of ["male" | "female" | "other"]')
    salary: int


class DbConnection:
    # TODO - Протестировать этот класс взамен использования глобальных переменных `_client`, `_db`, `_collection`

    def __init__(self, client_uri: str, db_name: str, collection_name: str):
        self.client_uri = client_uri
        self.db_name = db_name
        self.collection_name = collection_name
        self.client: AsyncIOMotorClient = None
        self.db: AsyncIOMotorDatabase = None
        self.collection: AsyncIOMotorCollection = None

    async def get_connection(self, client_uri: str = None, db_name: str = None,
                                collection_name: str = None) -> AsyncIOMotorCollection:
        """
        Создаем подключение к Базе данных. Если параметры не заданы - значит заполняем поля самого объекта.
        :param client_uri:
        :param db_name:
        :param collection_name:
        :return:
        """
        if client_uri:
            client = await AsyncIOMotorClient(client_uri)
            db = client[db_name]
            collection = db[collection_name]
        else:
            if self.client is None:     # Создаем подключение, если оно еще не было задано
                self.client = await AsyncIOMotorClient(client_uri)

            if db_name:     # Если передано новое имя БД - используем его.
                self.db = self.client[db_name]
            else:
                self.db = self.client[self.db_name]

            if collection_name:     # Если передано новое имя Коллекции - используем его.
                self.collection = self.db[collection_name]
            else:
                self.collection = self.db[self.collection_name]

            collection = self.collection

        print('Server connection was opened')
        return collection

    async def disconnect(self, client: AsyncIOMotorClient = None) -> None:
        if client is None and self.client is not None:
            await self.client.close()
            print('Server connection was closed')
        else:
            print('Connection not set')


# Вместо того чтобы прописать в `Settings` вложенный класс `Config`, проверяем наличие файла `.env` при инициализации.
if Path('.env').is_file():
    settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
else:
    settings = Settings()

app = FastAPI()

# TODO - заменить использование глобальных переменных на класс `DbConnection`.
_client = None
_db = None
_collection = None


# TODO - заменить использование этой функции на метод `DbConnection.get_connection()`.
def connect_to_db(client_uri=settings.client_uri, db_name=settings.db_name, collection_name=settings.collection_name):
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
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


# TODO - заменить использование этой функции на метод `DbConnection.disconnect()`.
def disconnect_from_db(client=_client):
    if client is not None:
        try:
            client.close()
            print('Server connection was closed')
        except Exception as e:
            print(e)


@app.on_event("startup")
async def startup():
    # TODO - Заменить на использование метода `DbConnection.get_connection()`.
    connect_to_db()


@app.on_event("shutdown")
async def shutdown():
    # TODO - Заменить на использование метода `DbConnection.disconnect()`.
    disconnect_from_db()


@app.get('/')
async def search_employees(company: str = None,
                           min_age: int = None,
                           max_age: int = None,
                           limit: int = None) -> list[ReturnModel]:
    # TODO - Реализовать Аутентификацию.
    # TODO - Реализовать фильтр с использованием сортировки по необходимым полям.
    query = {}
    if company:
        query['company'] = company

    if min_age and max_age and min_age > max_age:               # Защита от дурака
        min_age, max_age = max_age, min_age

    query_age = {}
    if min_age:
        query_age['$gt'] = min_age - 1          # Вычитаем единицу, т.к. функция mongodb возвращает значение БОЛЬШЕ

    if max_age:
        query_age['$lt'] = max_age + 1          # Добавляем единицу по аналогии с `min_age`

    if query_age:
        query['age'] = query_age

    """Вместо того, чтобы убрать лишь столбец `_id`, мы перечисляем все НЕОБХОДИМЫЕ столбцы.
    Это послужит защитой от передачи по ошибке чувствительных данных (номер карты, хеш пароля и т.п.)."""
    # TODO - реализовать передачу через параметры списка необходимых полей БД.
    columns = {'_id': 0, 'name': 1, 'email': 1, 'age': 1, 'company': 1, 'join_date': 1, 'job_title': 1,
               'gender': 1, 'salary': 1}
    search_filter = _collection.find(query, columns)

    if limit:
        search_filter = search_filter.limit(limit)

    employees = []
    try:
        employees = [ReturnModel(**employee) for employee in await search_filter.to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        print('Server Selection Timeout Error')
    except Exception as e:
        print(e)
        # todo - return `500`

    return employees
