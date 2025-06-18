from django.urls import path

from .views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    ExpenseListCreateView,
    ExpenseRetrieveUpdateDestroyView,
    ExpenseSummaryView,
)

urlpatterns = [
    path("categories/", CategoryListCreateView.as_view(), name="category-list"),
    path("categories/<int:pk>/", CategoryRetrieveUpdateDestroyView.as_view(), name="category-detail"),
    path("expenses/", ExpenseListCreateView.as_view(), name="expense-list"),
    path("expenses/<int:pk>/", ExpenseRetrieveUpdateDestroyView.as_view(), name="expense-detail"),
    path("summary/", ExpenseSummaryView.as_view(), name="expense-summary"),
]
