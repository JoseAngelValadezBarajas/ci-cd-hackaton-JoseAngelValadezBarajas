from django import forms
from .models import CustomUser, InventoryEntry, InventoryExit, Product

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.role_id = '2'  # Establecer el valor predeterminado como "Admin"
        if commit:
            user.save()
        return user
    
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'address']

class UserStatusForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    new_status = forms.ChoiceField(choices=CustomUser.role)

class UserEditForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput())
    new_username = forms.CharField(label='Nuevo nombre de usuario', max_length=150)
    new_email = forms.EmailField(label='Nuevo correo electrónico', max_length=254)
    new_role = forms.ChoiceField(label='Nuevo rol', choices=[(1, 'Admin'), (2, 'Consultor'), (3, 'Ventas')])

    def clean_new_email(self):
        new_email = self.cleaned_data.get('new_email')
        return new_email
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'stock', 'min_stock', 'price']

class StockForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['stock']

class InventoryEntryForm(forms.ModelForm):
    class Meta:
        model = InventoryEntry
        fields = ['product', 'quantity_received']

class InventoryExitForm(forms.ModelForm):
    class Meta:
        model = InventoryExit
        fields = ['product', 'quantity_sold']

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity_sold = cleaned_data.get('quantity_sold')

        if product and quantity_sold:
            if quantity_sold > product.stock:
                raise forms.ValidationError("No hay suficiente stock disponible para esta salida de inventario.")
            if product.stock - quantity_sold < product.min_stock:
                pass

        return cleaned_data

