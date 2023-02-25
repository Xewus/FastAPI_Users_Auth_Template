import json

import pytest
from fastapi.testclient import TestClient

from tests.helpers import base64image1, base64image2, base64image3

test_user_1 = {'username': 'user1', 'phone': 7_900_000_0001, 'password': 'password1', 'avatar': base64image1}
test_user_2 = {'username': 'user2', 'phone': 7_900_000_0002, 'password': 'password2', 'avatar': base64image2}


@pytest.mark.parametrize(
    'json, status_code',
    [
        (test_user_1, 200),
        (test_user_2, 200),
        ({'username': 'username busy', 'phone': 7_900_000_0003, 'password': 'password3', 'avatar': base64image3}, 400),
        ({'username': 'phone busy', 'phone': 7_900_000_0004, 'password': 'password4', 'avatar': base64image3}, 400),
        ({'username': 'phone short', 'phone': 7_900_000_005, 'password': 'password5', 'avatar': base64image3}, 422),
        ({'username': 'phone long', 'phone': 7_900_000_00006, 'password': 'password6', 'avatar': base64image3}, 422),
        ({'username': 'phone max', 'phone': 8_900_000_0007, 'password': 'password7', 'avatar': base64image3}, 422),
        ({'username': 'phone min', 'phone': 7_800_000_0008, 'password': 'password8', 'avatar': base64image3}, 422),
        ({'phone': 7_800_000_0009, 'password9': 'noUsername', 'avatar': base64image3}, 422),
        ({'username': 'no password', 'phone': 7_900_000_0010, 'avatar': base64image3}, 422),
        ({'username': 'no avatar', 'phone': 7_800_000_0011, 'password': 'password11'}, 422),
        ({'username': 'bad image', 'phone': 7_900_000_0012, 'password': 'password12', 'avatar': base64image3[:-1]}, 400),
    ]
)
def test_registration(
    http_client: TestClient, json: dict, status_code: int
):
    url = '/registration'
    http_client.post(url=url, json=json).status_code == status_code


def test_get_token(http_client: TestClient):
    http_client.post(url='/registration', json=test_user_1)
    url = '/token'

    # without password
    response = http_client.post(
        url=url,
        data={'username': test_user_1['phone']}
    )
    assert response.status_code == 422

    # incorrect password
    response = http_client.post(
        url=url,
        data={
            'username': test_user_1['phone'],
            'password': 'incorrect'
        }
    )
    assert response.status_code == 400

    response = http_client.post(
        url=url,
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password']
        }
    )
    assert response.status_code == 200

    data = json.loads(response.text)
    assert data['token_type'] == 'bearer'
    assert len(data['access_token']) > 1


def test_me(http_client: TestClient):
    # get token
    response = http_client.post(
        url='/token',
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password']
        }
    )
    data = json.loads(response.text)
    token_test_user = data['access_token']

    # without token
    url = '/users/me'
    assert http_client.get(url=url).status_code == 401

    response = http_client.get(
        url=url,
        headers={'Authorization': 'Bearer ' + token_test_user}
    )
    assert response.status_code == 200

    data = json.loads(response.text)
    assert data['username'] == test_user_1['username']
    assert data['phone'] == test_user_1['phone']
    assert data['is_active'] is True


def test_update_me(http_client: TestClient):
    # get token
    response = http_client.post(
        url='/token',
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password']
        }
    )
    data = json.loads(response.text)
    token_test_user = data['access_token']

    # without token
    url = '/users/me'
    assert http_client.patch(
        url=url,
        json={'username': 'update'}
    ).status_code == 401

    # update ok
    response = http_client.patch(
        url=url,
        json={'username': 'update'},
        headers={'Authorization': 'Bearer ' + token_test_user},
    )
    assert response.status_code == 200

    data = json.loads(response.text)
    assert data['username'] == 'update'

    # update not ok, username busy
    assert http_client.patch(
        url=url,
        json={'username': test_user_2['username']},
        headers={'Authorization': 'Bearer ' + token_test_user},
    ).status_code == 400

    response = http_client.get(
        url=url,
        headers={'Authorization': 'Bearer ' + token_test_user}
    )
    assert response.status_code == 200

    data = json.loads(response.text)
    assert data['username'] == 'update'
    assert data['phone'] == test_user_1['phone']
    assert data['is_active'] is True
