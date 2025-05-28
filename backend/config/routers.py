from rest_framework.routers import SimpleRouter
from payments.views import BankWebhookViewSet, OrganizationBalanceViewSet

router = SimpleRouter()

router.register(r"webhook/bank", BankWebhookViewSet, basename="bank-webhook")
router.register(r"organizations", OrganizationBalanceViewSet, basename="org-balance")
