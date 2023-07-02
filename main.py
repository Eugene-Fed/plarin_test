import uvicorn
from fastapi import FastAPI, HTTPException
from pymongo.errors import ServerSelectionTimeoutError
from pydantic_models import Settings, SearchModel, ReturnModel
from pathlib import Path
from db_filters import get_search_command
from db_connection import DbConnection
from typing import Any

if Path('.env').is_file():          # Если файл `.env` существует - забираем настройки из него
    settings = Settings(_env_file='.env', _env_file_encoding='utf-8')
else:                               # В противном случае пытаемся забрать настройки из системных переменных окружения.
    settings = Settings()

app = FastAPI()
connection = DbConnection(client_uri=settings.client_uri,
                          db_name=settings.db_name,
                          collection_name=settings.collection_name)


@app.on_event("startup")
def startup():
    connection()


@app.on_event("shutdown")
def shutdown():
    connection.disconnect_from_client()


@app.get('/search-by-get/', response_model=list[ReturnModel])
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
                        limit: int = None) -> Any:
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
    :return: Отфильтрованный и отсортированный `список JSON-объектов` БД
    """
    # TODO - Реализовать Аутентификацию.
    # TODO - Реализовать фильтр по списку значений для полей: Компания, Пол, Должность.

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
        employees = [ReturnModel(**employee) for employee in
                     await get_search_command(search_params, connection.collection).to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")

    return employees


@app.post('/search-by-post/', response_model=list[ReturnModel])
async def search_by_post(search_params: SearchModel) -> Any:
    """
    ## Доступ к списку сотрудников через POST-запрос.\n
    :param search_params: Формат входных данных для фильтра описан в `SearchModel`\n
    :return: Список отфильтрованных сотрудников. Формат выходных данных описан в `ReturnModel`\n
    """

    try:
        employees = [ReturnModel(**employee) for employee in await get_search_command(search_params,
                                                                                      connection.collection).to_list(None)]
        print(f'Number of found Employers: {len(employees)}')
    except ServerSelectionTimeoutError:
        raise HTTPException(status_code=504, detail="Server connection Timeout Error")

    return employees


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
