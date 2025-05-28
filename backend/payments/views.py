from rest_framework import viewsets, status
from rest_framework.response import Response
from django.db import transaction
from .models import Organization, Payment, BalanceLog
from .serializers import BankWebhookSerializer, OrganizationBalanceSerializer


class BankWebhookViewSet(viewsets.ViewSet):
    """
    POST /api/webhook/bank/ — Приём webhook-а от банка, создание платежа и начисление баланса.
    Только create (POST).
    """

    serializer_class = BankWebhookSerializer

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if Payment.objects.filter(operation_id=data["operation_id"]).exists():
            return Response(
                {"detail": "Операция уже обработана."}, status=status.HTTP_200_OK
            )

        with transaction.atomic():
            org, _ = Organization.objects.get_or_create(inn=data["payer_inn"])
            payment = Payment.objects.create(
                operation_id=data["operation_id"],
                amount=data["amount"],
                payer_inn=data["payer_inn"],
                document_number=data["document_number"],
                document_date=data["document_date"],
            )
            org.balance = org.balance + data["amount"]
            org.save(update_fields=["balance"])
            BalanceLog.objects.create(
                organization=org,
                payment=payment,
                amount=data["amount"],
                comment=f"Поступление по платёжке {payment.document_number}",
            )
        return Response(
            {"detail": "Платёж успешно обработан."}, status=status.HTTP_200_OK
        )


class OrganizationBalanceViewSet(viewsets.ViewSet):
    """
    GET /api/organizations/<inn>/balance/ — Получение баланса организации по ИНН.
    Только retrieve (GET).
    """

    serializer_class = OrganizationBalanceSerializer

    def retrieve(self, request, pk=None):
        try:
            org = Organization.objects.get(inn=pk)
        except Organization.DoesNotExist:
            return Response({"detail": "Организация не найдена."}, status=404)
        serializer = self.serializer_class(org)
        return Response(serializer.data)
