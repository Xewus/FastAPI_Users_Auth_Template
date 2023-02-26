## This is a simple template for FastAPI applications when user registration and authorization with a JWT token is required.

***
### Requirements
- Python 3.10 <=
- SQLAlchemy 2.0 <=
- Alembic
- Pytest

***
### Steps
```
git@github.com:Xewus/FastAPI_Users_Auth_Template.git
```
```
python3.10 -m venv venv
```
```
. venv/bin/activate
```
```
pip install -U pip && pip install -r requirements.txt
```
```
alembic upgrade head
```
```
pytest
```
```
uvicorn src.main:app --reload
```
