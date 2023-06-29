import motor.motor_asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from pymongo.errors import ServerSelectionTimeoutError
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from pydantic_models import Settings, SearchModel, ReturnModel
from pathlib import Path
from db_filters import get_filter_by_range, get_filter_by_string, get_search_command


if Path('.env').is_file():          # Если файл `.env` существует - забираем настройки из него
    settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
else:                               # В противном случае пытаемся забрать настройки из системных переменных окружения.
    settings = Settings()

app = FastAPI()

# TODO - заменить использование глобальных переменных на класс `db_connection.DbConnection`.
# Объекты подключения к БД.
_client: AsyncIOMotorClient = None
_db: AsyncIOMotorDatabase = None
_collection: AsyncIOMotorCollection = None


# БЛОК МЕТОДОВ ДЛЯ РАБОТЫ С ПОДКЛЮЧЕНИЕМ К БД #########################################################################
# При попытке вынести эти функции в отдельный модуль, тесты начинают падать из-за исключений, связанных с асинхронностью
def connect_to_db(client_uri=settings.client_uri, db_name=settings.db_name, collection_name=settings.collection_name):
    """
    # TODO - заменить использование этой функции на метод `db_connection.DbConnection.get_connection()`.
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


def disconnect_from_db(client=_client):
    """
    # TODO - заменить использование этой функции на метод `db_connection.DbConnection.disconnect()`.
    :param client:
    :return:
    """
    if client is not None:
        try:
            client.close()
            print('Server connection was closed')
        except Exception as e:
            print(e)


# БЛОК МЕТОДОВ FastAPI ################################################################################################
@app.on_event("startup")
async def startup():
    # TODO - Заменить на использование метода `db_connection.DbConnection.get_connection()`.
    connect_to_db()


@app.on_event("shutdown")
async def shutdown():
    # TODO - Заменить на использование метода `db_connection.DbConnection.disconnect()`.
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
        # raise HTTPException(status_code=404, detail=f'Collection "{settings.collection_name}" not found.')
        connect_to_db()

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
        employees = [ReturnModel(**employee) for employee in await get_search_command(search_params,
                                                                                      _collection).to_list(None)]
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
        # raise HTTPException(status_code=404, detail=f'Collection "{settings.collection_name}" not found.')
        connect_to_db()

    try:
        employees = [ReturnModel(**employee) for employee in await get_search_command(search_params,
                                                                                      _collection).to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")

    return employees


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
