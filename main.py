import motor.motor_asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pymongo.errors import ServerSelectionTimeoutError
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
    ## Используем для получения данных посредством POST запроса.
    """
    company: str | None = Field(default=None, description='Название компании')
    min_age: int | None = Field(default=None)                     # Минимальный возраст
    max_age: int | None = Field(default=None)                     # Максимальный возраст
    limit: int | None = Field(default=None, description='Лимит результатов выдачи')  # Лимит количества данных в выдаче
    name: str | None = None
    email: str | None = None
    start_join_date: str | None = Field(default=None, description='Дата в формате: `yyyy-MM-dd`')
    end_join_date: str | None = Field(default=None, description='Дата в формате: `yyyy-MM-dd`')
    job_title: str | None = None
    gender: str = Field(default=None, description='Одно из значений: `male`, `female`, `other`')
    min_salary: int | float | None = Field(default=None)
    max_salary: int | float | None = Field(default=None)
    sort_by: str | None = Field(default=None, description='Имя поля сортировки. Работает с любым полем (число и текст')
    sort_type: str | None = Field(default=None, description='`asc`: По возрастанию (default), `desc`: по убыванию')


class ReturnModel(BaseModel):
    """## Формат возвращаемых данных."""
    name: str = Field(description='ФИО Сотрудника')
    email: str
    age: int
    company: str
    join_date: str = Field(description='Дата в формате: `yyyy-MM-ddThh:mm:ssTZD`')
    job_title: str
    gender: str = Field(description='Одно из значений `male`, `female`, `other`')
    salary: int = Field(description='Зарплата в USD в Месяц =)')


class DbConnection:
    """ПОКА НЕ ИСПОЛЬЗУЕТСЯ"""
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
_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None
_collection: AsyncIOMotorCollection = None


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

    if min_val and type(min_val) == (int or float) \
            and max_val and type(max_val) == (int or float)\
            and min_val > max_val:
        # Меняем числа местами, если `min_val` > `max_val`
        min_val, max_val = max_val, min_val

    if min_val:
        query['$gte'] = min_val

    if max_val:
        query['$lte'] = max_val

    return query


def get_filter_by_string(name: str, value: str) -> dict:
    """
    Формируем часть запроса из текстовых или фильтров с возможностью обработки списка значений одного параметра.
    # TODO - Реализовать возможность принимать список значений в один параметр.
    :param name:
    :param value:
    :return: Результат выполнения метода AsyncIOMotorCollection.find()
    """
    query = {}
    if value is not None:
        query[name] = value
    return query


def get_search_command(search: SearchModel):
    """
    Формируем запрос к БД.
    :param search:
    :return:
    """
    query = {}

    """Обработка фильтра по строковым значениям"""
    # TODO - Сформировать словарь на основе названий и значений параметров класса `SearchModel`, взамен сопоставления.
    for key, value in {'company': search.company, 'job_title': search.job_title, 'gender': search.gender}.items():
        query.update(get_filter_by_string(name=key, value=value))

    """Обработка фильтра по числовым диапазонам"""
    if search.min_age or search.max_age:
        query['age'] = get_filter_by_range(min_val=search.min_age, max_val=search.max_age)
    if search.min_salary or search.max_salary:
        query['salary'] = get_filter_by_range(min_val=search.min_salary, max_val=search.max_salary)
    if search.start_join_date or search.end_join_date:
        query['join_date'] = get_filter_by_range(min_val=search.start_join_date, max_val=search.end_join_date)

    """Вместо того, чтобы убрать лишь столбец `_id`, мы перечисляем все НЕОБХОДИМЫЕ столбцы.
    Это послужит защитой от передачи по ошибке чувствительных данных (номер карты, хеш пароля и т.п.)."""
    # TODO - реализовать передачу через параметры списка необходимых полей БД.
    columns = {'_id': 0, 'name': 1, 'email': 1, 'age': 1, 'company': 1, 'join_date': 1, 'job_title': 1,
               'gender': 1, 'salary': 1}

    search_filter = _collection.find(query, columns)

    """Добавление лимитера по количеству данных в выдаче"""
    if search.limit:
        search_filter = search_filter.limit(search.limit)

    """Сортировка по полю"""
    if search.sort_by:
        if search.sort_type == 'desc':
            search_filter = search_filter.sort([[search.sort_by, -1]])
        else:
            search_filter = search_filter.sort([[search.sort_by, 1]])
    return search_filter


@app.on_event("startup")
async def startup():
    # TODO - Заменить на использование метода `DbConnection.get_connection()`.
    connect_to_db()


@app.on_event("shutdown")
async def shutdown():
    # TODO - Заменить на использование метода `DbConnection.disconnect()`.
    disconnect_from_db()


@app.get('/search-by-get/')
async def search_by_get(company: str = None,
                        min_age: int = None,
                        max_age: int = None,
                        min_salary: int = None,
                        max_salary: int = None,
                        job_title: str = None,
                        gender: str = None,
                        start_join_date: str = None,
                        end_join_date: str = None,
                        sort_by: str = None,
                        sort_type: str = None,
                        limit: int = None) -> list[ReturnModel]:
    """
    ## Доступ к списку сотрудников через GET-запрос. Формат выдачи описан ниже модуле `Schemas` / `ReturnModel`\n
    :param company: Название компании\n
    :param min_age: Минимальный возраст (включительно)\n
    :param max_age: Максимальный возраст (включительно)\n
    :param min_salary: Минимальная ЗП (включительно)\n
    :param max_salary: Максимальная ЗП (включительно)\n
    :param job_title: Должность\n
    :param gender: Один из вариантов: `male`, `female`, `other`\n
    :param start_join_date: Дата и время в формате `yyyy-MM-ddThh:mm:ssTZD`. Также работает формат `yyyy-MM-dd`\n
    :param end_join_date: Дата и время в формате `yyyy-MM-ddThh:mm:ssTZD`. Также работает формат `yyyy-MM-dd`\n
    :param sort_by: Поле, по которому необходимо делать сортировку. На выбор: `age`, `join_date`, `salary`\n
    :param sort_type: Направление сортировки: `asc` - по возрастанию (по-умолчанию) или `desc` - по убыванию\n
    :param limit: Количество данных в выдаче\n
    :return: Возвращаем `список JSON-объектов` БД
    """
    # TODO - Реализовать Аутентификацию.
    # TODO - Реализовать фильтр по списку значений для полей: Компания, Пол, Должность.
    if _collection is None:
        raise HTTPException(status_code=404, detail=f'Collection "{settings.collection_name}" not found.')

    # Переносим все полученные параметры в модель данных Pydantic.
    search_params = SearchModel(company=company,
                                min_age=min_age,
                                max_age=max_age,
                                min_salary=min_salary,
                                max_salary=max_salary,
                                job_title=job_title,
                                gender=gender,
                                start_join_date=start_join_date,
                                end_join_date=end_join_date,
                                sort_by=sort_by,
                                sort_type=sort_type,
                                limit=limit
                                )

    try:
        employees = [ReturnModel(**employee) for employee in await get_search_command(search_params).to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")

    return employees


@app.post('/search-by-post/')
async def search_by_post(search_params: SearchModel) -> list[ReturnModel]:
    """
    ## Доступ к списку сотрудников через POST-запрос.\n
    :param search_params: Формат входных данных для фильтра описан в `SearchModel`\n
    :return: Список отфильтрованных сотрудников. Формат выходных данных описан в `ReturnModel`\n
    """
    if _collection is None:
        raise HTTPException(status_code=404, detail=f'Collection "{settings.collection_name}" not found.')

    try:
        employees = [ReturnModel(**employee) for employee in await get_search_command(search_params).to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")

    return employees


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
