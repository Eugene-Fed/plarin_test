from fastapi import FastAPI, HTTPException
from pymongo.errors import ServerSelectionTimeoutError
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic import BaseModel, BaseSettings, Field
from pathlib import Path


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
    join_date: str | None = None                                        # TODO - валидировать формат даты
    job_title: str | list[str] | None = None
    gender: str = Field(default=None, description='One of ["male" | "female" | "other"]')
    min_salary: int | float | None = Field(default=None, gt=0)
    max_salary: int | float | None = Field(default=None, gt=0)
    sort: dict[str, int] | None = None                    # `1` - по возрастанию, `-1` - по убыванию


class ReturnModel(BaseModel):
    """Дата класс, представляющий формат возвращаемых данных"""
    name: str
    email: str
    age: int
    company: str
    join_date: str = Field(description='Date time in "yyyy-MM-ddThh:mm:ssTZD" format')
    job_title: str
    gender: str = Field(description='One of ["male" | "female" | "other"]')
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


# Вместо того чтобы прописать в `Settings` вложенный класс `Config`, используем `.env` только при его наличии
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
    :return: None
    """
    global _client
    global _db
    global _collection
    try:
        _client = motor.motor_asyncio.AsyncIOMotorClient(client_uri)
        _db = _client[db_name]
        _collection = _db[collection_name]

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


def get_filter_by_range(min_val: int | float | str = None,
                        max_val: int | float | str = None,
                        ) -> dict[str, int | float]:
    """
    Функция для форматирования числового фильтра.
    :param min_val: Минимальное значение.
    :param max_val: Максимальное значение.
    :return: Словарь с фильтром запроса к MongoDB.
    """
    query = {}

    if min_val and min_val.isnumeric() and max_val and max_val.isnumeric() and min_val > max_val:
        # Меняем числа местами, если `min_val` > `max_val`
        min_val, max_val = max_val, min_val

    if min_val:
        query['$gte'] = min_val

    if max_val:
        query['$lte'] = max_val

    return query


def get_filter_by_string(name: str, value: str) -> dict[str, str]:
    """
    Формируем часть запроса из текстовых или фильтров с возможностью обработки списка значений одного параметра.
    # TODO - Реализовать возможность принимать список значений в один параметр.
    :param name:
    :param value:
    :return:
    """
    query = {}
    if value is not None:
        query[name] = value
    return query


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
                           min_salary: int = None,
                           max_salary: int = None,
                           job_title: str = None,
                           gender: str = None,
                           start_join_date: str = None,
                           end_join_date: str = None,
                           limit: int = None) -> list[ReturnModel]:
    """
    Доступ к списку сотрудников. Формат выдачи описан ниже на странице документации в модуле `Schemas` / `ReturnModel`\n
    :param company: Название компании\n
    :param min_age: Минимальный возраст (включительно)\n
    :param max_age: Максимальный возраст (включительно)\n
    :param min_salary: Минимальная ЗП (включительно)\n
    :param max_salary: Максимальная ЗП (включительно)\n
    :param job_title: Должность\n
    :param gender: Один из вариантов: `male`, `female`, `other`\n
    :param start_join_date: Дата и время в формате `yyyy-MM-ddThh:mm:ssTZD`. Также работает формат `yyyy-MM-dd`\n
    :param end_join_date: Дата и время в формате `yyyy-MM-ddThh:mm:ssTZD`. Также работает формат `yyyy-MM-dd`\n
    :param limit: Количество данных в выдаче\n
    :return: Возвращаем список `JSON` объектов БД
    """
    # TODO - Реализовать Аутентификацию.
    # TODO - Реализовать фильтр по списку значений для полей: Компания, Пол, Должность.
    # TODO - Реализовать фильтр по дате устройства на работу с валидацией формата данных.
    query = {}

    """Обработка фильтра по строковым значениям"""
    for key, value in {'company': company, 'job_title': job_title, 'gender': gender}.items():
        query.update(get_filter_by_string(name=key, value=value))

    """Обработка фильтра по числовым диапазонам"""
    if min_age or max_age:
        query['age'] = get_filter_by_range(min_val=min_age, max_val=max_age)
    if min_salary or max_salary:
        query['salary'] = get_filter_by_range(min_val=min_salary, max_val=max_salary)
    if start_join_date or end_join_date:
        query['join_date'] = get_filter_by_range(min_val=start_join_date, max_val=end_join_date)

    """Вместо того, чтобы убрать лишь столбец `_id`, мы перечисляем все НЕОБХОДИМЫЕ столбцы.
    Это послужит защитой от передачи по ошибке чувствительных данных (номер карты, хеш пароля и т.п.)."""
    # TODO - реализовать передачу через параметры списка необходимых полей БД.
    columns = {'_id': 0, 'name': 1, 'email': 1, 'age': 1, 'company': 1, 'join_date': 1, 'job_title': 1,
               'gender': 1, 'salary': 1}
    search_filter = _collection.find(query, columns)

    """Добавление лимитера по количеству данных в выдаче"""
    if limit:
        search_filter = search_filter.limit(limit)

    # TODO - Реализовать фильтр с использованием сортировки по необходимым полям.

    employees = []
    try:
        employees = [ReturnModel(**employee) for employee in await search_filter.to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)

    return employees
