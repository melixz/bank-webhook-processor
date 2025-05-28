import pytest
from django.urls import reverse
from rest_framework.test import APIClient
import uuid

from payments.models import Payment, Organization

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def test_webhook_creates_payment_and_balance(api_client):
    """
    Проверяет, что webhook создаёт платёж и начисляет баланс организации.
    """
    url = reverse("bank-webhook-list")  # router url
    data = {
        "operation_id": str(uuid.uuid4()),
        "amount": 10000,
        "payer_inn": "1234567890",
        "document_number": "PAY-001",
        "document_date": "2024-04-27T21:00:00Z",
    }
    response = api_client.post(url, data, format="json")
    assert response.status_code == 200
    assert Payment.objects.filter(operation_id=data["operation_id"]).exists()
    org = Organization.objects.get(inn=data["payer_inn"])
    assert org.balance == data["amount"]


def test_webhook_idempotency(api_client):
    """
    Проверяет идемпотентность webhook: повторный запрос не увеличивает баланс и не создаёт дубликат платежа.
    """
    url = reverse("bank-webhook-list")
    op_id = str(uuid.uuid4())
    data = {
        "operation_id": op_id,
        "amount": 5000,
        "payer_inn": "1234567890",
        "document_number": "PAY-002",
        "document_date": "2024-04-27T21:00:00Z",
    }
    api_client.post(url, data, format="json")
    response = api_client.post(url, data, format="json")
    assert response.status_code == 200
    org = Organization.objects.get(inn=data["payer_inn"])
    assert org.balance == data["amount"]
    assert Payment.objects.filter(operation_id=op_id).count() == 1


def test_get_organization_balance(api_client):
    """
    Проверяет получение баланса организации по ИНН.
    """
    org = Organization.objects.create(inn="1234567890", balance=12345)
    url = reverse("org-balance-detail", args=[org.inn])
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.json() == {"inn": org.inn, "balance": org.balance}


def test_get_organization_balance_not_found(api_client):
    """
    Проверяет, что при запросе баланса несуществующей организации возвращается 404.
    """
    url = reverse("org-balance-detail", args=["0000000000"])
    response = api_client.get(url)
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"]
