from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from habits.models import Habit
from habits.serializers import HabitSerializer
from habits.validators import BaseValidator
from django.utils import timezone as djtz
from django.db import connection
from telegram_app.models import TelegramProfile
from habits.tasks import send_habit_reminders


User = get_user_model()


class HabitValidatorsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u", email="u@example.com", password="p"
        )
        self.pleasant = Habit.objects.create(
            user=self.user,
            place="home",
            time="10:00",
            action="tea",
            is_pleasant=True,
            periodicity=1,
            duration=60,
        )

    def fake_req(self):
        return type("r", (), {"user": self.user})

    def test_mutually_exclusive_reward_and_related(self):
        data = {
            "place": "park",
            "time": "12:00",
            "action": "walk",
            "is_pleasant": False,
            "related_habit": self.pleasant.id,
            "reward": "cake",
            "periodicity": 1,
            "duration": 60,
            "is_public": False,
        }
        s = HabitSerializer(data=data, context={"request": self.fake_req()})
        self.assertFalse(s.is_valid())
        self.assertIn("Нельзя одновременно указывать вознаграждение", str(s.errors))

    def test_pleasant_cannot_have_reward_or_related(self):
        data = {
            "place": "home",
            "time": "09:00",
            "action": "bath",
            "is_pleasant": True,
            "reward": "smth",
            "periodicity": 1,
            "duration": 60,
        }
        s = HabitSerializer(data=data, context={"request": self.fake_req()})
        self.assertFalse(s.is_valid())
        self.assertIn("У приятной привычки не может быть", str(s.errors))

    def test_related_must_be_pleasant(self):
        other = Habit.objects.create(
            user=self.user,
            place="gym",
            time="11:00",
            action="train",
            is_pleasant=False,
            periodicity=1,
            duration=60,
        )
        data = {
            "place": "park",
            "time": "12:00",
            "action": "walk",
            "is_pleasant": False,
            "related_habit": other.id,
            "periodicity": 1,
            "duration": 60,
        }
        s = HabitSerializer(data=data, context={"request": self.fake_req()})
        self.assertFalse(s.is_valid())
        self.assertIn(
            "В связанные привычки могут попадать только привычки", str(s.errors)
        )

    def test_periodicity_bounds(self):
        data = {
            "place": "p",
            "time": "12:00",
            "action": "a",
            "is_pleasant": False,
            "periodicity": 8,
            "duration": 60,
        }
        s = HabitSerializer(data=data, context={"request": self.fake_req()})
        self.assertFalse(s.is_valid())
        self.assertIn("периодичность должна быть от 1 до 7", str(s.errors))

    def test_max_duration(self):
        data = {
            "place": "p",
            "time": "12:00",
            "action": "a",
            "is_pleasant": False,
            "periodicity": 1,
            "duration": 121,
        }
        s = HabitSerializer(data=data, context={"request": self.fake_req()})
        self.assertFalse(s.is_valid())
        self.assertIn("не больше 120 секунд", str(s.errors))


class HabitViewsTest(APITestCase):
    def setUp(self):
        self.jwt_url = "/api/auth/jwt/create"
        self.list_url = "/api/habits/"
        self.public_url = "/api/habits/public/"

        self.u1 = User.objects.create_user(
            username="u1", email="u1@example.com", password="p"
        )
        self.u2 = User.objects.create_user(
            username="u2", email="u2@example.com", password="p"
        )

        tok1 = self.client.post(
            self.jwt_url, {"username": "u1", "password": "p"}, format="json"
        ).data
        tok2 = self.client.post(
            self.jwt_url, {"username": "u2", "password": "p"}, format="json"
        ).data
        self.a1 = tok1["access"]
        self.a2 = tok2["access"]

    def auth(self, access):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_crud_and_pagination(self):
        self.auth(self.a1)
        # create 6 habits to check pagination size=5
        for i in range(6):
            self.client.post(
                self.list_url,
                {
                    "place": "park",
                    "time": "10:0{}".format(i % 10),
                    "action": f"walk{i}",
                    "periodicity": 1,
                    "duration": 60,
                    "is_pleasant": False,
                },
                format="json",
            )
        r1 = self.client.get(self.list_url + "?page=1")
        r2 = self.client.get(self.list_url + "?page=2")
        self.assertEqual(r1.status_code, 200)
        self.assertEqual(r1.data["count"], 6)
        self.assertEqual(len(r1.data["results"]), 5)
        self.assertEqual(len(r2.data["results"]), 1)

        # update
        hid = r1.data["results"][0]["id"]
        ru = self.client.patch(
            f"{self.list_url}{hid}/", {"action": "newwalk"}, format="json"
        )
        self.assertEqual(ru.status_code, 200)
        self.assertEqual(ru.data["action"], "newwalk")

        # delete
        rd = self.client.delete(f"{self.list_url}{hid}/")
        self.assertIn(rd.status_code, (204, 200))

    def test_public_list_and_filters(self):
        self.auth(self.a2)
        self.client.post(
            self.list_url,
            {
                "place": "home",
                "time": "11:00",
                "action": "read",
                "periodicity": 1,
                "duration": 60,
                "is_pleasant": False,
                "is_public": True,
            },
            format="json",
        )
        self.client.post(
            self.list_url,
            {
                "place": "home",
                "time": "08:00",
                "action": "tea",
                "periodicity": 1,
                "duration": 60,
                "is_pleasant": True,
                "is_public": True,
            },
            format="json",
        )

        self.client.credentials()
        rp = self.client.get(self.public_url + "?is_pleasant=true&action=te")
        self.assertEqual(rp.status_code, 200)
        self.assertEqual(rp.data["count"], 1)

    def test_cannot_access_others_objects(self):
        self.auth(self.a2)
        h = self.client.post(
            self.list_url,
            {
                "place": "home",
                "time": "11:00",
                "action": "read",
                "periodicity": 1,
                "duration": 60,
                "is_pleasant": False,
            },
            format="json",
        ).data
        self.auth(self.a1)
        r = self.client.get(f"{self.list_url}{h['id']}/")
        self.assertEqual(r.status_code, 404)

class HabitModelStrTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="hs", email="hs@example.com", password="p")

    def test_str_useful_and_pleasant(self):
        h1 = Habit.objects.create(user=self.user, place="p", time="10:00", action="a", is_pleasant=False, periodicity=1, duration=60)
        h2 = Habit.objects.create(user=self.user, place="p", time="11:00", action="b", is_pleasant=True, periodicity=1, duration=60)
        self.assertIn("useful", str(h1))
        self.assertIn("pleasant", str(h2))

class BaseValidatorTest(TestCase):
    def test_base_validator_call_and_fields(self):
        class Dummy(BaseValidator):
            fields = ("x",)

        # __fields__ возвращает fields
        self.assertEqual(Dummy.__fields__(), ("x",))
        # вызов базового должен падать с NotImplementedError
        with self.assertRaises(NotImplementedError):
            BaseValidator()({"a": 1})

class ReminderExtraBranchesTest(APITestCase):
    @patch("habits.tasks.send_telegram_message")
    def test_reminder_skips_without_profile(self, send_mock):
        u = User.objects.create_user(username="no_profile", email="np@example.com", password="p")
        now = timezone.localtime()
        Habit.objects.create(user=u, place="park", time=now.strftime("%H:%M:%S"), action="walk", periodicity=1, duration=60)
        send_habit_reminders()
        # должно ничего не отправить, так как нет telegram_profile
        send_mock.assert_not_called()

    @patch("habits.tasks.send_telegram_message")
    def test_reminder_skips_not_due_today(self, send_mock):
        u = User.objects.create_user(username="not_due", email="nd@example.com", password="p")
        TelegramProfile.objects.create(user=u, chat_id="777")
        now = timezone.localtime()
        # periodicity=7 => не сегодня, если created_at окажется сегодня + delta%7==0 может совпасть,
        # поэтому создадим со вчерашней датой и periodicity=2, а тест запустится в день, который не кратен 2 от вчера
        h = Habit.objects.create(user=u, place="park", time=now.strftime("%H:%M:%S"), action="walk", periodicity=3, duration=60)
        # вручную поправим created_at на дату, чтобы delta%3 != 0
        yesterday = djtz.localdate()  # сегодня
        # сдвигаем на +1 день назад в БД (создаём ситуацию delta=0, что кратно 3) — чтобы избежать совпадения, лучше на +2
        with connection.cursor() as cur:
            cur.execute("UPDATE habits_habit SET created_at = created_at - interval '2 days' WHERE id = %s", [h.id])
        send_mock.reset_mock()
        send_habit_reminders()
        # может отправиться или нет в зависимости от даты; чтобы гарантировать отсутствие, подберем periodicity=4 и -2 дня => delta%4=2
        # Пересоздадим корректно:
        Habit.objects.filter(id=h.id).delete()
        h = Habit.objects.create(user=u, place="park", time=now.strftime("%H:%M:%S"), action="walk", periodicity=4, duration=60)
        with connection.cursor() as cur:
            cur.execute("UPDATE habits_habit SET created_at = created_at - interval '2 days' WHERE id = %s", [h.id])
        send_mock.reset_mock()
        send_habit_reminders()
        send_mock.assert_not_called()
