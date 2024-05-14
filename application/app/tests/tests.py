from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Role

class RoleModelTestCase(TestCase):
    def test_default_role(self):

        default_role = Role.default_role()

        self.assertEqual(default_role.name, 'Consultor')

class CustomUserManagerTestCase(TestCase):
    def test_create_user(self):
        user = get_user_model().objects.create_user(
            email='test@example.com',
            username='testuser',
            password='password123',
            first_name='John',
            last_name='Doe',
            address='123 Main St',
        )

        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('password123'))
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.address, '123 Main St')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)


class CustomUserModelTestCase(TestCase):
    def test_str_method(self):
        user = get_user_model().objects.create_user(
            email='test@example.com',
            username='testuser',
            password='password123',
            first_name='John',
            last_name='Doe',
            address='123 Main St',
        )

        self.assertEqual(str(user), 'test@example.com')
