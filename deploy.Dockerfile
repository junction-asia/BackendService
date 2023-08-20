FROM python:3.9.9

COPY . .

RUN pip install poetry
RUN POETRY_VIRTUALENVS_CREATE=false poetry install --no-root


CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

EXPOSE 8000
