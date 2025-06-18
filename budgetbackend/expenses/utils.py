from budgetbackend.expenses.models import Category


def create_user_category(user, system_category):
    return Category.objects.create(name=system_category.name, user=user)
