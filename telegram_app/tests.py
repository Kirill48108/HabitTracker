from unittest.mock import patch

import requests
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIRequestFactory, APITestCase, force_authenticate

from habits.models import Habit
from telegram_app import services as tg_services
from telegram_app.models import TelegramProfile
from telegram_app.views import TelegramProfileUpsertView

User = get_user_model()


class TelegramProfileTest(APITestCase):
    def setUp(self):
        self.jwt_url = "/api/auth/jwt/create"
        self.url = "/api/telegram/profile/"
        self.u = User.objects.create_user(username="u", email="u@example.com", password="p")
        tok = self.client.post(self.jwt_url, {"username": "u", "password": "p"}, format="json").data
        self.access = tok["access"]

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_upsert_profile(self):
        self.auth()
        r1 = self.client.post(self.url, {"chat_id": "12345"}, format="json")
        self.assertEqual(r1.status_code, 201)
        r2 = self.client.post(self.url, {"chat_id": "12345"}, format="json")
        self.assertEqual(r2.status_code, 201)


class ReminderTaskTest(APITestCase):
    @patch("habits.tasks.send_telegram_message")
    def test_send_habit_reminders(self, send_mock):
        u = User.objects.create_user(username="r", email="r@example.com", password="p")
        # создать профиль
        from telegram_app.models import TelegramProfile

        TelegramProfile.objects.create(user=u, chat_id="555")
        # создать привычку на текущее время
        now = timezone.localtime()
        time_str = now.strftime("%H:%M:%S")
        Habit.objects.create(
            user=u,
            place="park",
            time=time_str,
            action="walk",
            periodicity=1,
            duration=60,
        )
        # выполнить задачу
        from habits.tasks import send_habit_reminders

        send_habit_reminders()
        self.assertTrue(send_mock.called)


class TelegramServicesTest(APITestCase):
    @patch("telegram_app.services.requests.post")
    def test_send_message_no_token_and_success_and_exception(self, post_mock):
        # без токена — не должен вызывать post
        orig_token = tg_services.TELEGRAM_BOT_TOKEN
        tg_services.TELEGRAM_BOT_TOKEN = ""
        tg_services.send_telegram_message("1", "hi")
        post_mock.assert_not_called()

        # с токеном — успешный запрос
        tg_services.TELEGRAM_BOT_TOKEN = "x"
        post_mock.reset_mock()
        tg_services.send_telegram_message("1", "hi")
        post_mock.assert_called_once()

        # с токеном и кастомным parse_mode
        post_mock.reset_mock()
        tg_services.send_telegram_message("1", "<b>hi</b>", parse_mode="Markdown")
        post_mock.assert_called_once()
        args, kwargs = post_mock.call_args
        assert kwargs["json"]["parse_mode"] == "Markdown"

        # выброс исключения — не должен упасть
        post_mock.reset_mock()
        post_mock.side_effect = requests.RequestException("boom")
        tg_services.send_telegram_message("1", "fail")
        post_mock.assert_called_once()

        # восстановим токен
        tg_services.TELEGRAM_BOT_TOKEN = orig_token


class TelegramModelStrTest(APITestCase):
    def test_str(self):
        u = User.objects.create_user(username="tg", email="tg@example.com", password="p")
        p = TelegramProfile.objects.create(user=u, chat_id="999")
        self.assertIn("999", str(p))


class TelegramViewGetQuerysetTest(APITestCase):
    def test_get_queryset(self):
        u = User.objects.create_user(username="v", email="v@example.com", password="p")
        factory = APIRequestFactory()
        request = factory.get("/api/telegram/profile/")
        force_authenticate(request, user=u)
        view = TelegramProfileUpsertView()
        view.request = request
        qs = view.get_queryset()
        self.assertEqual(qs.count(), 0)
