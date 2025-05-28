# bank-webhook-processor

Backend-сервис для приема и обработки webhook-ов от банка с учетом баланса организаций по ИНН.

## Технологии

- Python 3.12
- Django 5.2.1
- MySQL
- Django REST Framework
- Pytest, pytest-django (для тестирования)
- Ruff (линтер)

## Описание

Сервис реализует два основных эндпоинта:

### POST `/api/webhook/bank/`

- Принимает webhook-и от банка в формате:
  ```json
  {
    "operation_id": "ccf0a86d-041b-4991-bcf7-e2352f7b8a4a",
    "amount": 145000,
    "payer_inn": "1234567890",
    "document_number": "PAY-328",
    "document_date": "2024-04-27T21:00:00Z"
  }
  ```
- Поведение:
  - Если операция с таким `operation_id` уже существует — возвращает `200 OK`, баланс не изменяется (защита от дублей).
  - Если операция новая:
    - Создаёт запись `Payment`.
    - Начисляет сумму на баланс организации с соответствующим `payer_inn`.
    - Логирует изменение баланса (в отдельной таблице или через логирование).

### GET `/api/organizations/<inn>/balance/`

- Возвращает текущий баланс организации по ИНН:
  ```json
  {
    "inn": "1234567890",
    "balance": 145000
  }
  ```

## Структура

- `Organization` — модель организации с ИНН и балансом.
- `Payment` — модель платежа с уникальным `operation_id`.
- `BalanceLog` — (опционально) лог изменений баланса.

## Настройка

1. Установите [uv](https://github.com/astral-sh/uv):

```bash
# На Linux/macOS через curl
curl -LsSf https://astral.sh/uv/install.sh | sh
# или через pipx
pipx install uv
```

2. Создайте виртуальное окружение и активируйте его:

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows
```

3. Установите зависимости проекта:

```bash
uv sync
```

## Тесты

Тесты расположены в директории `backend/tests/`.

Для запуска тестов используйте команду:
```bash
pytest
```
