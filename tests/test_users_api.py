import json

import pytest
from fastapi.testclient import TestClient

from tests.helpers.b64_images import base64image1, base64image2, base64image3

test_user_1 = {'username': 'user1', 'phone': 7_900_000_0001, 'password': 'password01', 'avatar': base64image1}
test_user_2 = {'username': 'user2', 'phone': 7_900_000_0002, 'password': 'password02', 'avatar': base64image2}


@pytest.mark.parametrize('json, status_code', [(test_user_1, 201), (test_user_2, 201)])
def test_set_users(http_client: TestClient, json: dict, status_code: int):
    url = '/registration'
    response = http_client.post(url=url, json=json)
    assert response.status_code == status_code, response.text


@pytest.fixture(name='app_with_users')
def set_users(http_client: TestClient) -> TestClient:
    url = '/registration'
    http_client.post(url=url, json=test_user_1)
    http_client.post(url=url, json=test_user_2)
    return http_client


@pytest.mark.parametrize(
    'json, status_code',
    [
        ({'username': 'user1',       'phone': 7_900_000_0003,  'password': 'usernam busy', 'avatar': base64image3    }, 400),
        ({'username': 'phone busy',  'phone': 7_900_000_0001,  'password': 'password04',   'avatar': base64image3    }, 400),
        ({'username': 'phone short', 'phone': 7_900_000_005, '  password': 'password05',   'avatar': base64image3    }, 422),
        ({'username': 'phone long',  'phone': 7_900_000_00006, 'password': 'password06',   'avatar': base64image3    }, 422),
        ({'username': 'phone max',   'phone': 8_900_000_0007,  'password': 'password07',   'avatar': base64image3    }, 422),
        ({'username': 'phone min',   'phone': 7_800_000_0008,  'password': 'password08',   'avatar': base64image3    }, 422),
        ({                           'phone': 7_800_000_0009,  'password': 'noUsername',   'avatar': base64image3    }, 422),
        ({'username': 'no phone',                              'password': 'password10',   'avatar': base64image3    }, 422),
        ({'username': 'no password', 'phone': 7_900_000_0011,                              'avatar': base64image3    }, 422),
        ({'username': 'no avatar',   'phone': 7_800_000_0012,  'password': 'password12'                              }, 422),
        ({'username': 'bad image',   'phone': 7_900_000_0013,  'password': 'password13',   'avatar': base64image3[1:]}, 422),
    ]
)
def test_registration(
    app_with_users: TestClient, json: dict, status_code: int
):
    url = '/registration'
    response = app_with_users.post(url=url, json=json)
    assert response.status_code == status_code, response.text


def test_get_token(app_with_users: TestClient):
    app_with_users.post(url='/registration', json=test_user_1)
    url = '/token'

    # without password
    response = app_with_users.post(
        url=url,
        data={'username': test_user_1['phone']}
    )
    assert response.status_code == 422, response.text

    # incorrect password
    response = app_with_users.post(
        url=url,
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password'][1:]
        }
    )
    assert response.status_code == 400, response.text

    response = app_with_users.post(
        url=url,
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password']
        }
    )
    assert response.status_code == 200, response.text

    data = json.loads(response.text)
    assert data['token_type'] == 'bearer'
    assert len(data['access_token']) > 1


def test_me(app_with_users: TestClient):
    # without token
    url = '/users/me'
    response = app_with_users.get(url=url)
    assert response.status_code == 401, response.text

    # get token
    response = app_with_users.post(
        url='/token',
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password']
        }
    )
    data = json.loads(response.text)
    token_test_user = data['access_token']

    # with token
    response = app_with_users.get(
        url=url,
        headers={'Authorization': 'Bearer ' + token_test_user}
    )
    assert response.status_code == 200, response.text

    data = json.loads(response.text)
    assert data['username'] == test_user_1['username']
    assert data['phone'] == test_user_1['phone']
    assert data['is_active'] is True


def test_update_me(app_with_users: TestClient):
    # without token
    url = '/users/me'
    response = app_with_users.patch(
        url=url,
        json={'username': 'update'}
    )
    assert response.status_code == 401, response.text

    # get token
    response = app_with_users.post(
        url='/token',
        data={
            'username': test_user_1['phone'],
            'password': test_user_1['password']
        }
    )
    data = json.loads(response.text)
    token_test_user = data['access_token']

    # ########################## username ####################### #
    # update not ok, bad username
    response = app_with_users.patch(
        url=url,
        json={'username': 'up'},
        headers={'Authorization': 'Bearer ' + token_test_user},
    )
    assert response.status_code == 422, response.text

    # update not ok, username busy
    response = app_with_users.patch(
        url=url,
        json={'username': test_user_2['username']},
        headers={'Authorization': 'Bearer ' + token_test_user},
    )
    assert response.status_code == 400, response.text

    # update username ok
    response = app_with_users.patch(
        url=url,
        json={'username': 'update'},
        headers={'Authorization': 'Bearer ' + token_test_user},
    )
    assert response.status_code == 202, response.text

    # ########################### avatar ######################## #
    # update not ok, bad avatar
    response = app_with_users.patch(
        url=url,
        json={'avatar': 'base64image'},
        headers={'Authorization': 'Bearer ' + token_test_user},
    )
    assert response.status_code in (400, 422), response.text

    # update avatar ok
    response = app_with_users.patch(
        url=url,
        json={'avatar': base64image2},
        headers={'Authorization': 'Bearer ' + token_test_user},
    )
    assert response.status_code == 202, response.text

    # check user after updates
    response = app_with_users.get(
        url=url,
        headers={'Authorization': 'Bearer ' + token_test_user}
    )
    assert response.status_code == 200, response.text

    data = json.loads(response.text)
    assert data['username'] == 'update'
    assert data['phone'] == test_user_1['phone']
    assert data['is_active'] is True
