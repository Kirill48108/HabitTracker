from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

from .filters import HabitFilter
from .models import Habit
from .permissions import IsOwner
from .serializers import HabitSerializer


class HabitViewSet(viewsets.ModelViewSet):
    serializer_class = HabitSerializer
    permission_classes = [IsOwner]
    filterset_class = HabitFilter

    def get_queryset(self):
        return Habit.objects.filter(user=self.request.user).order_by("-id")

    @action(detail=False, methods=["get"], url_path="public", permission_classes=[AllowAny])
    def public_list(self, request):
        qs = Habit.objects.filter(is_public=True).order_by("-id")
        # Включаем django-filter и остальные бекенды фильтрации/поиска/ordering
        qs = self.filter_queryset(qs)
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
