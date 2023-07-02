from os import environ
from pydantic import BaseModel, BaseSettings, Field, EmailStr


class Settings(BaseSettings):
    """
    Параметры подключения к ДБ из переменных окружения.
    # TODO - Реализовать импорт данных из системных переменных, если файл .env отсутствует.
    """
    app_name: str = 'GetEmployees'
    client_uri: str = environ.get('CLIENT_URI')
    db_name: str = environ.get('DB_NAME')
    collection_name: str = environ.get('employees_test')
    db_auth: str = environ.get('DB_AUTH')


class SearchModel(BaseModel):
    """
    ## Используем для получения данных посредством POST запроса.
    """
    company: str | None = Field(default=None, description='Название компании')
    min_age: int | None = Field(default=None)                     # Минимальный возраст
    max_age: int | None = Field(default=None)                     # Максимальный возраст
    limit: int | None = Field(default=None, description='Лимит результатов выдачи')  # Лимит количества данных в выдаче
    name: str | None = None
    email: EmailStr | None = None
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
    # !!! НЕ ВЫВОДИТЬ ЧУВСТВИТЕЛЬНЫЕ ДАННЫЕ !!!
    name: str = Field(description='ФИО Сотрудника')
    email: str          # !!! EmailStr - кладет тесты !!!
    age: int
    company: str
    join_date: str = Field(description='Дата в формате: `yyyy-MM-ddThh:mm:ssTZD`')
    job_title: str
    gender: str = Field(description='Одно из значений `male`, `female`, `other`')
    salary: int = Field(description='Зарплата в USD в Месяц =)')

