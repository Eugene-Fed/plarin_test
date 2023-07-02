from main import app, connection, startup, settings
from fastapi.testclient import TestClient
import pytest
from httpx import AsyncClient
import asyncio

client = TestClient(app)
startup()
params = {'max_age': 55,
          'min_salary': 3500,
          'max_salary': 7000,
          'job_title': 'janitor',
          'gender': 'male',
          'start_join_date': '2010-10-29',
          'end_join_date': '2015-01-01',
          'sort_by': 'age',
          'sort_type': 'desc',
          'limit': 2
          }
response_json = [
                  {
                    "name": "Lev Cash",
                    "email": "Sed@nisiMaurisnulla.co.uk",
                    "age": 47,
                    "company": "Google",
                    "join_date": "2014-10-12T22:05:09-07:00",
                    "job_title": "janitor",
                    "gender": "male",
                    "salary": 3751
                  },
                  {
                    "name": "Mohammad Mccall",
                    "email": "adipiscing@ipsumCurabitur.com",
                    "age": 41,
                    "company": "LinkedIn",
                    "join_date": "2011-02-18T10:40:17-08:00",
                    "job_title": "janitor",
                    "gender": "male",
                    "salary": 6393
                  }
                ]


def test_get_company_age():
    response = client.get('/search-by-get/', params=params)
    assert response.status_code == 200
    assert response.json() == response_json
