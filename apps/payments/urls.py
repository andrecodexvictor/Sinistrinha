from django.urls import path
from .views import DepositView, WithdrawView, TransactionHistoryView

urlpatterns = [
    path('deposit/', DepositView.as_view(), name='payments_deposit'),
    path('withdraw/', WithdrawView.as_view(), name='payments_withdraw'),
    path('transactions/', TransactionHistoryView.as_view(), name='payments_history'),
]
