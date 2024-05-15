from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


#Modelos para usuario y rol
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def default_role(cls):
        return cls.objects.get_or_create(name='Consultor')[0]  

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, role=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        if role is None:
            role = Role.default_role()  
        user = self.model(email=email, username=username, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address = models.TextField()
    role = models.ForeignKey(Role, on_delete=models.CASCADE)  

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  

    def __str__(self):
        return self.email

#Modelos para producto, entrada de inventario y salida de inventario       
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    stock = models.IntegerField()
    min_stock = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
    
class InventoryEntry(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_received = models.IntegerField()
    date_received = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.date_received}"
    
class InventoryExit(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_sold = models.IntegerField()
    date_sold = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.date_sold}"
    
class InsufficientStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity_needed = models.IntegerField(null=True)

    def __str__(self):
        if self.quantity_needed is not None:
            return f"{self.product.name} - {self.quantity_needed} needed"
        else:
            return f"{self.product.name} - No quantity needed"

#Modelo de ticket
class Ticket(models.Model):
    TYPE_CHOICES = [
        ('Soporte', 'Soporte'),
        ('Errores', 'Errores'),
        ('Dudas', 'Dudas'),
        ('Cuenta', 'Cuenta'),
    ]
    status = models.CharField(max_length=100)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

#Señales para stock
@receiver(post_save, sender=InventoryEntry)
def update_product_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock += instance.quantity_received
        product.save()

@receiver(post_save, sender=InventoryExit)
def update_product_stock_on_exit(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.stock -= instance.quantity_sold
        product.save()

@receiver(post_delete, sender=InventoryExit)
def update_product_stock_on_exit_delete(sender, instance, **kwargs):
    product = instance.product
    product.stock += instance.quantity_sold
    product.save()

@receiver(post_save, sender=Product)
def check_insufficient_stock(sender, instance, **kwargs):
    if instance.stock < instance.min_stock:
        quantity_needed = instance.min_stock - instance.stock
        print(quantity_needed)
        if quantity_needed is not None:
            insufficient_stock, created = InsufficientStock.objects.get_or_create(product=instance)
            insufficient_stock.quantity_needed = quantity_needed
            insufficient_stock.save()
    else:
        InsufficientStock.objects.filter(product=instance).delete()


