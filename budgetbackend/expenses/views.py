from datetime import datetime

from django.db.models import Q, Sum
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Expense
from .serializers import CategorySerializer, ExpenseSerializer


class CategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Category.objects.none()  # Return empty queryset for docs
        return Category.objects.filter(Q(user=self.request.user) | Q(user__isnull=True))

    def perform_create(self, serializer):
        # Check if creating from system category
        system_category_id = self.request.data.get("system_category_id")
        if system_category_id:
            system_category = get_object_or_404(Category, id=system_category_id, user__isnull=True)
            serializer.save(
                user=self.request.user,
                name=system_category.name,
            )
        else:
            # Normal category creation
            serializer.save(user=self.request.user)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_description="List all categories with optional search",
        manual_parameters=[
            openapi.Parameter(
                "search", openapi.IN_QUERY, description="Search categories by name", type=openapi.TYPE_STRING
            )
        ],
        responses={200: CategorySerializer(many=True), 401: "Unauthorized"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_description="Create a new category",
        request_body=CategorySerializer,
        responses={201: CategorySerializer, 400: "Invalid input data", 401: "Unauthorized"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Category.objects.none()  # Return empty queryset for docs
        return Category.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_description="Retrieve a specific category by ID",
        responses={200: CategorySerializer, 401: "Unauthorized", 404: "Category not found"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_description="Fully update a category",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: "Invalid input data",
            401: "Unauthorized",
            404: "Category not found",
        },
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_description="Partially update a category",
        request_body=CategorySerializer,
        responses={
            200: CategorySerializer,
            400: "Invalid input data",
            401: "Unauthorized",
            404: "Category not found",
        },
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Categories"],
        operation_description="Delete a category",
        responses={204: "No content (successful deletion)", 401: "Unauthorized", 404: "Category not found"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        "category": ["exact"],
        "amount": ["gte", "lte"],
    }
    search_fields = ["description"]
    ordering_fields = ["amount", "created_at"]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Expense.objects.none()
        return Expense.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        tags=["Expenses"], operation_description="Retrieve a list of all expenses with filtering options"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Expenses"],
        operation_description="Create a new expense record",
        request_body=ExpenseSerializer,
        responses={201: ExpenseSerializer, 400: "Invalid input data"},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ExpenseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Expense.objects.none()
        return Expense.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        tags=["Expenses"],
        operation_description="Retrieve a specific expense by ID",
        responses={200: ExpenseSerializer, 400: "Expense not found"},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Expenses"],
        operation_description="Update an existing expense",
        request_body=ExpenseSerializer,
        responses={200: ExpenseSerializer, 400: "Invalid input data", 404: "Expense not found"},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Expenses"],
        operation_description="Partially update an existing expense",
        request_body=ExpenseSerializer,
        responses={200: ExpenseSerializer, 400: "Invalid input data", 404: "Expense not found"},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["Expenses"],
        operation_description="Delete an expense",
        responses={204: "No content (successful deletion)", 404: "Expense not found"},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ExpenseSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Expenses"],
        operation_description="Get expense summary statistics",
        manual_parameters=[
            openapi.Parameter(
                "period",
                openapi.IN_QUERY,
                description="Time period for summary (month/quarter/year)",
                type=openapi.TYPE_STRING,
                enum=["month", "quarter", "year"],
                default="month",
            )
        ],
        responses={
            200: openapi.Response(
                description="Expense summary data",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "total": openapi.Schema(type=openapi.TYPE_NUMBER, description="Total expenses"),
                        "by_category": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "category__name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "total": openapi.Schema(type=openapi.TYPE_NUMBER),
                                },
                            ),
                        ),
                        "period": openapi.Schema(type=openapi.TYPE_STRING),
                        "period_start": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
                    },
                ),
            )
        },
    )
    def get(self, request):
        time_period = request.query_params.get("period", "month")
        now = datetime.now()

        expenses = Expense.objects.filter(user=request.user)

        if time_period == "month":
            expenses = expenses.filter(created_at__year=now.year, created_at__month=now.month)
            date_from = now.replace(day=1)
        elif time_period == "quarter":
            current_quarter = (now.month - 1) // 3 + 1
            start_month = 3 * (current_quarter - 1) + 1
            date_from = now.replace(month=start_month, day=1)
            expenses = expenses.filter(
                created_at__year=now.year,
                created_at__month__gte=start_month,
                created_at__month__lt=start_month + 3,
            )
        elif time_period == "year":
            expenses = expenses.filter(created_at__year=now.year)
            date_from = now.replace(month=1, day=1)
        else:
            date_from = None

        total = expenses.aggregate(total=Sum("amount"))["total"] or 0
        by_category = expenses.values("category__name").annotate(total=Sum("amount")).order_by("-total")

        return Response(
            {
                "total": total,
                "by_category": by_category,
                "period": time_period,
                "period_start": date_from,
            }
        )
