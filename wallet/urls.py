from django.urls import path
from .views import WalletListCreateView, LoanListCreateView, TransactionListCreateView

urlpatterns = [
    path('wallets/', WalletListCreateView.as_view(), name='wallet-list-create'),
    path('loans/', LoanListCreateView.as_view(), name='loan-list-create'),
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
]
