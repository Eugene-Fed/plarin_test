from pydantic_models import SearchModel
from motor.motor_asyncio import AsyncIOMotorCollection


def get_filter_by_range(min_val: int | float | str = None,
                        max_val: int | float | str = None,
                        ) -> dict[str, int | float]:
    """
    Генерация фильтра по числовым диапазонам.\n
    :param min_val: Минимальное значение.
    :param max_val: Максимальное значение.
    :return: Словарь с фильтром запроса к MongoDB с числовыми параметрами.
    """
    query = {}

    if min_val and type(min_val) == (int or float) \
            and max_val and type(max_val) == (int or float)\
            and min_val > max_val:
        # Пытался проверять через тип через `.isnumeric`, но тесты генерят Исключения при работе с этим методом.
        min_val, max_val = max_val, min_val     # Меняем числа местами, если `min_val` > `max_val`

    if min_val:
        query['$gte'] = min_val                 # Добавляем к запросу метод "Больше или равно"

    if max_val:
        query['$lte'] = max_val                 # Добавляем к запросу метод "Меньше или равно"

    return query


def get_filter_by_string(name: str, value: str) -> dict:
    """
    Генерация фильтра по текстовым параметрам.
    # TODO - Реализовать возможность принимать список значений в один параметр.\n
    :param name: Имя параметра, например `company`.
    :param value: Значение параметра, например `Yandex`.
    :return: Словарь с фильтром запроса к MongoDB с текстовыми параметрами.
    """
    query = {}
    if value is not None:
        query[name] = value
    return query


def get_search_command(search: SearchModel, collection: AsyncIOMotorCollection):
    """
    Формируем поисковый запрос к БД на основе списка параметров `GET`-запроса или json-тела `POST`-запроса.
    :param search: Параметры запроса в формате Базовой модели `pydantic`. Формат описан в модуле pydantic_models.\n
    :param collection:
    :return: Объект запроса к MongoDB.
    """
    query = {}

    """Обработка фильтра по строковым значениям"""
    # TODO - Сформировать словарь на основе названий и значений параметров класса `SearchModel`, взамен сопоставления.
    for name, value in {'company': search.company, 'job_title': search.job_title, 'gender': search.gender}.items():
        query.update(get_filter_by_string(name=name, value=value))

    """Обработка фильтра по числовым диапазонам"""
    if search.min_age or search.max_age:
        query['age'] = get_filter_by_range(min_val=search.min_age, max_val=search.max_age)
    if search.min_salary or search.max_salary:
        query['salary'] = get_filter_by_range(min_val=search.min_salary, max_val=search.max_salary)
    if search.start_join_date or search.end_join_date:
        query['join_date'] = get_filter_by_range(min_val=search.start_join_date, max_val=search.end_join_date)

    '''Выключаем из выдачи столбец с ID, который имеет встроенный тип MongoDB и приводит к ошибке.
    За сохранность чувствительных данных отвечает класс `pydantic_models.ReturnModel`'''
    columns = {'_id:': 0}
    search_filter = collection.find(query, columns)

    """Добавление лимитера по количеству данных в выдаче"""
    if search.limit:
        search_filter = search_filter.limit(search.limit)

    """Сортировка по полю"""
    if search.sort_by:
        if search.sort_type == 'desc':              # Если задано - сортируем по убыванию.
            search_filter = search_filter.sort([[search.sort_by, -1]])
        else:                                       # Во всех прочих случаях сортируем по возрастанию.
            search_filter = search_filter.sort([[search.sort_by, 1]])
    return search_filter
