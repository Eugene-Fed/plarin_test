from pydantic import BaseModel, BaseSettings, Field


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
