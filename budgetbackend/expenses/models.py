from _decimal import Decimal
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="categories",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "user")
        verbose_name_plural = "categories"

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="expenses")
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="expenses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.description} - {self.amount} ({self.created_at})"

    def clean(self):
        if self.category.user != self.user:
            raise ValidationError("Category does not belong to this user")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
