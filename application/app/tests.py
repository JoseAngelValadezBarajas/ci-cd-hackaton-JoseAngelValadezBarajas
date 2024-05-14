from typing import Self
from django.test import TestCase
from django.contrib.auth import get_user_model
from app.views import InsufficientStockListAPIView, InventoryEntryCreateAPIView, InventoryEntryListAPIView, InventoryExitCreateAPIView, InventoryExitListAPIView, ProductDetailAPIView, ProductStockAPIView
from .serializers import CustomUserSerializer, LoginSerializer, ProfileSerializer, ProductSerializer, InventoryEntrySerializer, InventoryExitSerializer
from .models import CustomUser, InsufficientStock, Product, InventoryEntry, InventoryExit, Role
from django.utils import timezone
from .form import CustomUserCreationForm, InventoryExitForm
from rest_framework import status
from rest_framework.test import APIClient, force_authenticate, APIRequestFactory



##Test para user

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

##Test para producto

class ProductModelTestCase(TestCase):
    def test_str_method(self):
        product = Product.objects.create(
            name='Camisa',
            description='Una camisa elegante',
            stock=10,
            min_stock=5,
            price=20.99
        )
        self.assertEqual(str(product), 'Camisa')

class InventoryEntryModelTestCase(TestCase):
    def test_str_method(self):
        product = Product.objects.create(
            name='Camisa',
            description='Una camisa elegante',
            stock=10,
            min_stock=5,
            price=20.99
        )
        entry = InventoryEntry.objects.create(
            product=product,
            quantity_received=5
        )
        self.assertEqual(str(entry), f'Camisa - {entry.date_received}')

class InventoryExitModelTestCase(TestCase):
    def test_str_method(self):
        product = Product.objects.create(
            name='Camisa',
            description='Una camisa elegante',
            stock=10,
            min_stock=5,
            price=20.99
        )
        exit = InventoryExit.objects.create(
            product=product,
            quantity_sold=2
        )
        self.assertEqual(str(exit), f'Camisa - {exit.date_sold}')

class InsufficientStockModelTestCase(TestCase):
    def test_str_method_quantity_needed(self):
        product = Product.objects.create(
            name='Camisa',
            description='Una camisa elegante',
            stock=10,
            min_stock=5,
            price=20.99
        )
        insufficient_stock = InsufficientStock.objects.create(
            product=product,
            quantity_needed=3
        )
        self.assertEqual(str(insufficient_stock), 'Camisa - 3 needed')

##Test para las señales

class SignalsTestCase(TestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Producto de prueba', description='Descripción del producto', stock=100, min_stock=10, price=50.0)

    def test_update_product_stock_signal(self):
        entry = InventoryEntry.objects.create(product=self.product, quantity_received=50, date_received=timezone.now())
        self.assertEqual(self.product.stock, 150)

    def test_update_product_stock_on_exit_signal(self):
        exit = InventoryExit.objects.create(product=self.product, quantity_sold=20, date_sold=timezone.now())
        self.assertEqual(self.product.stock, 80)

    def test_update_product_stock_on_exit_delete_signal(self):
        exit = InventoryExit.objects.create(product=self.product, quantity_sold=20, date_sold=timezone.now())
        self.assertEqual(self.product.stock, 80)
        exit.delete()
        self.assertEqual(self.product.stock, 100)

##Test para los serializadores

User = get_user_model()

class CustomUserSerializerTestCase(TestCase):
    def test_valid_data(self):
        data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'address': '123 Main St',
            'password': 'password123'
        }
        serializer = CustomUserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        invalid_data = {
            'email': 'invalid-email',
            'username': '',
            'first_name': 'Test',
            'last_name': 'User',
            'address': '123 Main St',
            'password': 'password123'
        }
        serializer = CustomUserSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class ProfileSerializerTestCase(TestCase):
    def test_valid_data(self):
        user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'address': '123 Main St',
            'role_id': 1,  # Ajusta este valor según sea necesario
        }
        serializer = ProfileSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())

class ProductSerializerTestCase(TestCase):
    def test_valid_data(self):
        data = {
            'name': 'Product 1',
            'description': 'Description of Product 1',
            'stock': 10,
            'min_stock': 5,
            'price': '10.00'
        }
        serializer = ProductSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        invalid_data = {
            'name': '',
            'description': 'Description of Product 1',
            'stock': 10,
            'min_stock': 5,
            'price': '10.00'
        }
        serializer = ProductSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class InventoryEntrySerializerTestCase(TestCase):
    def test_valid_data(self):
        product = Product.objects.create(name='Product 1', description='Description of Product 1', stock=10, min_stock=5, price='10.00')
        data = {
            'product': product.id,
            'quantity_received': 5
        }
        serializer = InventoryEntrySerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        invalid_data = {
            'product': '',
            'quantity_received': 5
        }
        serializer = InventoryEntrySerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class InventoryExitSerializerTestCase(TestCase):
    def test_valid_data(self):
        product = Product.objects.create(name='Product 1', description='Description of Product 1', stock=10, min_stock=5, price='10.00')
        data = {
            'product': product.id,
            'quantity_sold': 5
        }
        serializer = InventoryExitSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_data(self):
        invalid_data = {
            'product': '',
            'quantity_sold': 5
        }
        serializer = InventoryExitSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())

class LoginSerializerTestCase(TestCase):
    def setUp(self):
        self.role = Role.objects.create(id=1, name='Test Role')  
    def test_valid_data(self):
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpassword',
            first_name='Test',
            last_name='User',
            address='123 Main St',
            role=self.role  
        )
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword',
        }
        serializer = LoginSerializer(data=login_data)
        self.assertTrue(serializer.is_valid())

##Test para los form

class TestForms(TestCase):
    def test_clean_password2(self):
        form_data = {'password1': 'test123', 'password2': 'test123'}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clean_password2_mismatch(self):
        form_data = {'password1': 'test123', 'password2': 'test456'}
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['password2'], ['Las contraseñas no coinciden'])

    def test_save_user(self):
        form_data = {'username': 'test_user', 'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com', 'password1': 'test123', 'password2': 'test123'}
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save(commit=False)
        self.assertEqual(user.username, 'test_user')
        self.assertEqual(user.email, 'test@example.com')

    def test_clean_quantity_sold_valid(self):
        product = Product.objects.create(name='Test Product', description='Test Description', stock=10, min_stock=5, price=100)
        form_data = {'product': product, 'quantity_sold': 5}
        form = InventoryExitForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_clean_quantity_sold_invalid(self):
        product = Product.objects.create(name='Test Product', description='Test Description', stock=10, min_stock=5, price=100)
        form_data = {'product': product, 'quantity_sold': 15}
        form = InventoryExitForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'], ['No hay suficiente stock disponible para esta salida de inventario.'])

##Test Para API
#AQUI HABIA UN USER MODEL
class TestLogin(TestCase):
    def setUp(self):
        self.role = Role.objects.create(id=1, name='Test Role')  
        self.user_data = {'email': 'test@example.com', 'username': 'test_user', 'password': 'test123'}
        self.user = User.objects.create_user(**self.user_data)

    def test_register_view(self):
        response = self.client.post('/register/', self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_view(self):
        response = self.client.post('/login/', {'email': 'test@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response)

class TestProfileViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name='Test Role')
        self.user_data = {'email': 'test@example.com', 'username': 'test_user', 'password': 'test123', 'role': self.role}
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_profile_edit_view(self):
        url = '/api/profile/edit/'
        data = {'first_name': 'Updated First Name', 'last_name': 'Updated Last Name', 'address': 'Updated Address'}
        self.client.force_login(self.user)
        response = self.client.put(url, data, format='json')  
        self.assertEqual(response.status_code, 200)  
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated First Name')
        self.assertEqual(self.user.last_name, 'Updated Last Name')
        self.assertEqual(self.user.address, 'Updated Address')

class ProductCreateAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.role = Role.objects.create(name='Test Role', id=1)  
        self.user = CustomUser.objects.create_user(email='test@example.com', username='test_user', password='test_password', role=self.role)

    def test_post_with_authenticated_user(self):
        url = '/api/products/create/'
        data = {'name': 'Test Product', 'description': 'Test Description', 'stock': 10, 'min_stock': 5, 'price': '10.00'}
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, data, format='json')
        if self.user.role_id == 1:  
            self.assertEqual(response.status_code, 201)
        else:
            self.assertEqual(response.status_code, 403)

class ProductDetailAPIViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='test@example.com', username='test_user', password='test_password')
        self.product = Product.objects.create(name='Test Product', description='Test Description', stock=10, min_stock=5, price='10.00')

    def test_get_existing_product(self):
        url = f'/api/products/{self.product.pk}/'
        request = self.factory.get(url)
        request.user = self.user
        force_authenticate(request, user=self.user)
        view = ProductDetailAPIView.as_view()
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

class ProductStockAPIViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email = 'test@example.com',username='testuser', password='testpassword')
        self.product = Product.objects.create(name='Test Product', description='Test Description', stock=10, min_stock=5, price='10.00')
    def test_get_product_stock(self):
        url = f'/api/products/{self.product.pk}/stock/'
        request = self.factory.get(url)
        force_authenticate(request, user=self.user)  
        view = ProductStockAPIView.as_view()
        response = view(request, pk=self.product.pk)
        self.assertEqual(response.status_code, 200)

class InventoryEntryCreateAPIViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='test@example.com', username='test_user', password='test_password')
        self.product = Product.objects.create(name='Test Product', description='Test Description', stock=10, min_stock=5, price='10.00')
    def test_create_inventory_entry(self):
        url = '/api/inventory/entry/create/'
        data = {'product': self.product.id, 'quantity_received': 10}
        request = self.factory.post(url, data, format='json')
        request.user = self.user
        force_authenticate(request, user=self.user)
        response = InventoryEntryCreateAPIView.as_view()(request)
        self.assertEqual(response.status_code, 201)

class InventoryExitCreateAPIViewTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = User.objects.create_user(email='test@example.com', username='test_user', password='test_password')
        self.product = Product.objects.create(name='Test Product', description='Test Description', stock=10, min_stock=5, price='10.00')
    def test_create_inventory_exit(self):
        url = '/api/inventory/exit/create/'
        data = {'product': self.product.id, 'quantity_sold': 5}
        request = self.factory.post(url, data, format='json')
        request.user = self.user
        force_authenticate(request, user=self.user)
        response = InventoryExitCreateAPIView.as_view()(request)
        self.assertEqual(response.status_code, 201)

class InventoryEntryListAPIViewTestCase(TestCase):
    def test_get_inventory_entries(self):
        self.user = User.objects.create_user(email = 'test@example.com',username='testuser', password='testpassword')
        url = '/api/inventory/entry/list/'
        request = APIRequestFactory().get(url)
        force_authenticate(request, user=self.user)
        response = InventoryEntryListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

class InventoryExitListAPIViewTestCase(TestCase):
    def test_get_inventory_exits(self):
        self.user = User.objects.create_user(email = 'test@example.com',username='testuser', password='testpassword')
        url = '/api/inventory/exit/list/'
        request = APIRequestFactory().get(url)
        force_authenticate(request, user=self.user)
        response = InventoryExitListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)

class InsufficientStockListAPIViewTestCase(TestCase):
    def test_get_insufficient_stocks(self):
        self.user = User.objects.create_user(email = 'test@example.com',username='testuser', password='testpassword')
        url = '/api/insufficient/stock/list/'
        request = APIRequestFactory().get(url)
        force_authenticate(request, user=self.user)
        response = InsufficientStockListAPIView.as_view()(request)
        self.assertEqual(response.status_code, 200)



