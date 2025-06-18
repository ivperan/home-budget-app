# tests/test_models.py
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from expenses.models import Category, Expense

User = get_user_model()


class CategoryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_category_creation(self):
        category = Category.objects.create(
            name='Food',
            user=self.user
        )
        self.assertEqual(category.name, 'Food')
        self.assertEqual(category.user, self.user)

    def test_category_str_representation(self):
        category = Category.objects.create(name='Food', user=self.user)
        self.assertEqual(str(category), f"Food ({self.user.username})")

    def test_unique_together_constraint(self):
        Category.objects.create(name='Food', user=self.user)
        with self.assertRaises(ValidationError):
            # Should fail due to unique_together constraint
            duplicate_category = Category(name='Food', user=self.user)
            duplicate_category.full_clean()


class ExpenseModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Food',
            user=self.user
        )

    def test_expense_creation(self):
        expense = Expense.objects.create(
            description='Lunch',
            amount=Decimal('15.50'),
            category=self.category,
            user=self.user
        )
        self.assertEqual(expense.description, 'Lunch')
        self.assertEqual(expense.amount, Decimal('15.50'))

    def test_expense_validation_category_user_mismatch(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        other_category = Category.objects.create(
            name='Transport',
            user=other_user
        )

        with self.assertRaises(ValidationError):
            expense = Expense(
                description='Wrong category',
                amount=Decimal('10.00'),
                category=other_category,
                user=self.user
            )
            expense.save()  # This should trigger clean() and raise ValidationError
