from main import app, connection, startup, settings
from fastapi.testclient import TestClient

client = TestClient(app)
startup()


def test_get_endpoint():
    connection.get_client_connection()
    response = client.get('/search-by-get/')
    # connection.disconnect_from_client()
    assert response.status_code == 200


def test_post_endpoint():
    connection.get_client_connection()
    response = client.post('/search-by-post/', json={})
    assert response.status_code == 200
'''

def test_get_company_age():
    # connect_to_db()
    params = {'company': 'Yandex', 'min_age': 20, 'max_age': 20}
    response_json = [{"name": "Michael Mays",
                      "email": "augue.scelerisque@aliquetvel.edu",
                      "age": 20,
                      "company": "Yandex",
                      "join_date": "2014-12-05T14:33:25-08:00",
                      "job_title": "manager",
                      "gender": "other",
                      "salary": 3773}]
    response = client.get('/search-by-get/', params=params)
    assert response.status_code == 200
    assert response.json() == response_json


def test_post_company_age():
    # connect_to_db()
    params = {'company': 'Yandex', 'min_age': 20, 'max_age': 20}
    response_json = [{"name": "Michael Mays",
                      "email": "augue.scelerisque@aliquetvel.edu",
                      "age": 20,
                      "company": "Yandex",
                      "join_date": "2014-12-05T14:33:25-08:00",
                      "job_title": "manager",
                      "gender": "other",
                      "salary": 3773}]
    response = client.post('/search-by-post/', json=params)
    assert response.status_code == 200
    assert response.json() == response_json


def test_get_limit_sort():
    # connect_to_db()
    params = {'company': 'Google', 'limit': 1, 'sort_by': 'age', 'sort_type': 'desc'}
    response_json = [{"name": "Callum Bird",
                      "email": "ipsum.dolor.sit@gravidaAliquam.edu",
                      "age": 70,
                      "company": "Google",
                      "join_date": "1997-10-13T04:59:58-07:00",
                      "job_title": "manager",
                      "gender": "female",
                      "salary": 9813}]
    response = client.get('/search-by-get/', params=params)
    assert response.status_code == 200
    assert response.json() == response_json


def test_post_limit_sort():
    # connect_to_db()
    params = {'company': 'Google', 'limit': 1, 'sort_by': 'age', 'sort_type': 'desc'}
    response_json = [{"name": "Callum Bird",
                      "email": "ipsum.dolor.sit@gravidaAliquam.edu",
                      "age": 70,
                      "company": "Google",
                      "join_date": "1997-10-13T04:59:58-07:00",
                      "job_title": "manager",
                      "gender": "female",
                      "salary": 9813}]
    response = client.post('/search-by-post/', json=params)
    assert response.status_code == 200
    assert response.json() == response_json


def test_get_job_gender_date_salary():
    # connect_to_db()
    params = {'min_salary': 4000, 'max_salary': 6000, 'job_title': 'director',
              'gender': 'female', 'start_join_date': '2010-01-01', 'end_join_date': '2011-01-01'}
    response_json = [{"name": "Ivan Higgins",
                      "email": "hendrerit.Donec@arcu.co.uk",
                      "age": 57,
                      "company": "Plarin",
                      "join_date": "2010-11-30T15:33:00-08:00",
                      "job_title": "director",
                      "gender": "female",
                      "salary": 5720}]
    response = client.get('/search-by-get/', params=params)
    assert response.status_code == 200
    assert response.json() == response_json


def test_post_job_gender_date_salary():
    # connect_to_db()
    params = {'min_salary': 4000, 'max_salary': 6000, 'job_title': 'director',
              'gender': 'female', 'start_join_date': '2010-01-01', 'end_join_date': '2011-01-01'}
    response_json = [{"name": "Ivan Higgins",
                      "email": "hendrerit.Donec@arcu.co.uk",
                      "age": 57,
                      "company": "Plarin",
                      "join_date": "2010-11-30T15:33:00-08:00",
                      "job_title": "director",
                      "gender": "female",
                      "salary": 5720}]
    response = client.post('/search-by-post/', json=params)
    assert response.status_code == 200
    assert response.json() == response_json
'''