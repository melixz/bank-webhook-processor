from django.db import models


class Organization(models.Model):
    """
    Модель организации.
    Хранит ИНН и текущий баланс организации в копейках.
    Используется для идентификации и учёта средств по ИНН.
    """

    inn = models.CharField(max_length=12, unique=True, verbose_name="ИНН")
    balance = models.BigIntegerField(default=0, verbose_name="Баланс (в копейках)")

    def __str__(self):
        return f"{self.inn} (Баланс: {self.balance})"


class Payment(models.Model):
    """
    Модель платежа, поступившего через webhook банка.
    Содержит уникальный идентификатор операции, сумму, ИНН плательщика,
    номер и дату документа. Используется для защиты от дублей и учёта поступлений.
    """

    operation_id = models.UUIDField(unique=True, verbose_name="ID операции")
    amount = models.BigIntegerField(verbose_name="Сумма (в копейках)")
    payer_inn = models.CharField(max_length=12, verbose_name="ИНН плательщика")
    document_number = models.CharField(max_length=64, verbose_name="Номер документа")
    document_date = models.DateTimeField(verbose_name="Дата документа")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operation_id} | {self.amount} | {self.payer_inn}"


class BalanceLog(models.Model):
    """
    Лог изменений баланса организации.
    Фиксирует каждое изменение баланса (например, поступление платежа),
    ссылается на организацию и платеж, хранит сумму изменения и комментарий.
    """

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="balance_logs"
    )
    payment = models.ForeignKey(
        Payment, on_delete=models.CASCADE, null=True, blank=True
    )
    amount = models.BigIntegerField(verbose_name="Изменение баланса (в копейках)")
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return f"{self.organization.inn}: {self.amount} ({self.created_at})"
