from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models


class User(AbstractUser):
    initial_balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=1000.00, validators=[MinValueValidator(0)]
    )

    @property
    def current_balance(self):
        """Calculate current balance without direct Expense import"""
        if not hasattr(self, "_current_balance"):
            total_expenses = self.expenses.aggregate(total=models.Sum("amount"))["total"] or 0
            self._current_balance = self.initial_balance - total_expenses
        return self._current_balance

    def __str__(self):
        return self.username
