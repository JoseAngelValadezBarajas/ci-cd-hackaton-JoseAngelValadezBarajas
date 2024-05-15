from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, InsufficientStock, InventoryEntry, InventoryExit, Product


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id','email', 'username', 'first_name', 'last_name', 'address','role_id', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    msg = 'La cuenta está desactivada.'
                    raise serializers.ValidationError(msg)
            else:
                msg = 'No se pudo iniciar sesión con las credenciales proporcionadas.'
                raise serializers.ValidationError(msg)
        else:
            msg = 'Se debe proporcionar el correo electrónico y la contraseña.'
            raise serializers.ValidationError(msg)

        return data
    
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'address']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class InventoryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryEntry
        fields = '__all__'

class InventoryExitSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryExit
        fields = '__all__'

class InsufficientStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsufficientStock
        fields = '__all__'

