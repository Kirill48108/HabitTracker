from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import TelegramProfile
from .serializers import TelegramProfileSerializer


class TelegramProfileUpsertView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TelegramProfileSerializer

    def get_queryset(self):
        # Возвращаем пустой queryset, если request/user отсутствует или не аутентифицирован
        req = getattr(self, "request", None)
        user = getattr(req, "user", None)
        if not user or not getattr(user, "is_authenticated", False):
            return TelegramProfile.objects.none()
        return TelegramProfile.objects.filter(user=user)
