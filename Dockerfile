FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN pip install poetry

WORKDIR /http_metadata_inventory_service

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --without dev

COPY . .

EXPOSE 8000

CMD ["python3", "main.py"]
