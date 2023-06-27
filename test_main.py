import json
from main import app, connect_to_db
from fastapi import FastAPI
from fastapi.testclient import TestClient

client = TestClient(app)
connect_to_db()


def test_search_main():
    response = client.get('/')
    assert response.status_code == 200


def test_search_company_age():
    # TODO - разобраться с ошибкой `RuntimeError: Event loop is closed` во время работы `pytest`.
    # todo - при ручном тестировании все работает, но `pytest` валится на описанном ниже запросе.
    get_params = {'company': 'Yandex', 'min_age': 20, 'max_age': 20}
    response_json = [
                      {
                        "name": "Michael Mays",
                        "email": "augue.scelerisque@aliquetvel.edu",
                        "age": 20,
                        "company": "Yandex",
                        "join_date": "2014-12-05T14:33:25-08:00",
                        "job_title": "manager",
                        "gender": "other",
                        "salary": 3773
                      }
                    ]
    response = client.get('/', params=get_params)
    assert response.status_code == 200
    assert response.json() == response_json
