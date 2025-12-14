from django.urls import path

from .views import TelegramProfileUpsertView

urlpatterns = [
    path("profile/", TelegramProfileUpsertView.as_view(), name="telegram-profile"),
]
