# test main application

from fastapi import FastAPI
from fastapi.testclient import TestClient

from aiida_restapi.config import API_CONFIG


def test_read_only_mode(read_only_app: FastAPI):
    client = TestClient(read_only_app)
    response = client.get('/computers/')
    assert response.status_code == 200
    response = client.post('/computers/', json={'name': 'new_computer'})
    assert response.status_code == 405


def test_route_redirects(app: FastAPI):
    client = TestClient(app)
    response = client.get('/')
    assert response.status_code == 200
    assert '/endpoints' in response.url.path
    response = client.get(API_CONFIG['PREFIX'])
    assert response.status_code == 200
    assert '/endpoints' in response.url.path
