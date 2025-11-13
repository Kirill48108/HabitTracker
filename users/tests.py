from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APITestCase, APIRequestFactory
from users.serializers import RegisterSerializer, ChangePasswordSerializer


User = get_user_model()


class UserModelTest(TestCase):
    def test_str_and_unique_email(self):
        u = User.objects.create_user(
            username="u1", email="u1@example.com", password="p"
        )
        self.assertIn("u1@example.com", str(u))
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="u2", email="u1@example.com", password="p"
            )


class UsersApiTest(APITestCase):
    def setUp(self):
        self.register_url = "/api/auth/register/"
        self.jwt_url = "/api/auth/jwt/create"
        self.refresh_url = "/api/auth/jwt/refresh"
        self.me_url = "/api/auth/me/"
        self.change_pwd_url = "/api/auth/password/change/"

    def auth(self, access: str):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_register_login_me_and_change_password(self):
        r = self.client.post(
            self.register_url,
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "S3cretpass!",
            },
            format="json",
        )
        self.assertEqual(r.status_code, 201)

        r2 = self.client.post(
            self.jwt_url,
            {"username": "alice", "password": "S3cretpass!"},
            format="json",
        )
        self.assertEqual(r2.status_code, 200)
        access, refresh = r2.data["access"], r2.data["refresh"]
        self.assertTrue(access and refresh)

        self.auth(access)
        r3 = self.client.get(self.me_url)
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.data["email"], "alice@example.com")

        r4 = self.client.patch(self.me_url, {"first_name": "Al"}, format="json")
        self.assertEqual(r4.status_code, 200)
        self.assertEqual(r4.data["first_name"], "Al")

        r5 = self.client.post(
            self.change_pwd_url,
            {"current_password": "S3cretpass!", "new_password": "N3wStrongPass!"},
            format="json",
        )
        self.assertEqual(r5.status_code, 204)

        # старый access может считаться валидным до истечения, проверим вход новым паролем
        r6 = self.client.post(
            self.jwt_url,
            {"username": "alice", "password": "N3wStrongPass!"},
            format="json",
        )
        self.assertEqual(r6.status_code, 200)

        r7 = self.client.post(self.refresh_url, {"refresh": refresh}, format="json")
        self.assertEqual(r7.status_code, 200)


class UsersSerializerEdgeCasesTest(APITestCase):
    def test_register_duplicate_email(self):
        User.objects.create_user(username="a", email="dup@example.com", password="p")
        s = RegisterSerializer(data={"username": "b", "email": "dup@example.com", "password": "p"})
        self.assertFalse(s.is_valid())
        self.assertIn("email", s.errors)

    def test_change_password_invalid_current(self):
        u = User.objects.create_user(username="c", email="c@example.com", password="p")
        factory = APIRequestFactory()
        request = factory.post("/api/auth/password/change/", {"current_password": "wrong", "new_password": "Newpass123!"}, format="json")
        request.user = u
        s = ChangePasswordSerializer(data={"current_password": "wrong", "new_password": "Newpass123!"}, context={"request": request})
        self.assertFalse(s.is_valid())
        self.assertIn("current_password", s.errors)
