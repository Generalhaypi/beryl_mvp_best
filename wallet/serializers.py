from rest_framework import serializers
from .models import Wallet, Loan, Transaction


# ----- Sérialiseur pour le portefeuille -----
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'user', 'balance', 'created_at']


# ----- Sérialiseur pour les prêts -----
class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['id', 'wallet', 'principal', 'balance', 'interest_rate', 'status']


# ----- Sérialiseur pour les transactions -----
class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'wallet', 'amount', 'type', 'label', 'created_at']
