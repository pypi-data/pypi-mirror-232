from django.test import TestCase
from users.models import CustomUser


class CustomUserTestCase(TestCase):
    def setUp(self) -> None:
        pass

    def test_create_user(self) -> None:
        print("Testing: Create User ")
        user = CustomUser.objects.create_user("testuser@test.com", "testpass")
        self.assertEqual(user.email, "testuser@test.com")
        self.assertTrue(isinstance(user, CustomUser))

    def test_create_admin(self) -> None:
        print("Testing: Create Admin")
        user = CustomUser.objects.create_admin(
            "testadmin@test.com", "adminpass")
        self.assertEqual(user.email, "testadmin@test.com")
        self.assertTrue(user.is_admin)

    def test_create_superuser(self) -> None:
        print("Testing: Create SuperUser")
        user = CustomUser.objects.create_superuser(
            "testsuperuser@test.com", "superpass")
        self.assertEqual(user.email, "testsuperuser@test.com")
        self.assertTrue(user.is_superuser)
