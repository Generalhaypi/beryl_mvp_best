from django.conf import settings
from django.db import models


# Modèle principal du portefeuille (Wallet)
class Wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallets'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Portefeuille {self.user} - {self.balance}"


# Modèle des prêts (Loan)
class Loan(models.Model):
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    principal = models.DecimalField(max_digits=10, decimal_places=2)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return f"Prêt {self.principal} - {self.status}"


# Modèle des transactions (Transaction)
class Transaction(models.Model):
    TYPE_CHOICES = (
        ('Credit', 'Credit'),
        ('Debit', 'Debit'),
    )

    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=6, choices=TYPE_CHOICES)
    label = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.amount} - {self.wallet}"
