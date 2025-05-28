from rest_framework import serializers
from .models import Organization


class BankWebhookSerializer(serializers.Serializer):
    """
    Сериализатор для входящего webhook-а от банка.
    Используется для создания платежа и начисления баланса организации.
    """

    operation_id = serializers.UUIDField()
    amount = serializers.IntegerField(min_value=1)
    payer_inn = serializers.CharField(max_length=12, min_length=10)
    document_number = serializers.CharField(max_length=64)
    document_date = serializers.DateTimeField()

    def validate_payer_inn(self, value):
        """
        Проверяет корректность ИНН (10 или 12 цифр).
        """
        if not value.isdigit() or len(value) not in (10, 12):
            raise serializers.ValidationError(
                "ИНН должен содержать только 10 или 12 цифр."
            )
        return value


class OrganizationBalanceSerializer(serializers.ModelSerializer):
    """
    Сериализатор для возврата текущего баланса организации по ИНН.
    Используется в GET /api/organizations/<inn>/balance/.
    """

    class Meta:
        model = Organization
        fields = ("inn", "balance")
