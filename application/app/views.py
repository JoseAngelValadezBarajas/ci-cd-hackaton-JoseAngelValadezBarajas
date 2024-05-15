from rest_framework import status
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import Http404, JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import CustomUser, InsufficientStock, InventoryEntry, InventoryExit, Ticket, Product
from .form import CustomUserCreationForm, CustomUserForm, InventoryEntryForm, InventoryExitForm, UserStatusForm, UserEditForm, ProductForm, StockForm
from app.serializers import CustomUserSerializer, InsufficientStockSerializer, InventoryEntrySerializer, InventoryExitSerializer, LoginSerializer, ProductSerializer

@login_required 
def create_ticket(request):
    if request.method == 'POST':
        try:
            type = request.POST.get('type')
            description = request.POST.get('description')
            status = 'Pendiente'
            ticket = Ticket.objects.create(type=type, description=description, status=status)
            return JsonResponse({'message': 'Ticket creado correctamente'}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
@login_required 
def get_tickets(request):
    if request.method == 'GET':
        tickets = Ticket.objects.all().values()
        return JsonResponse({'tickets': list(tickets)})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
@login_required 
def get_ticket_details(request, ticket_id):
    if request.method == 'GET':
        try:
            ticket = Ticket.objects.get(id=ticket_id)
            return JsonResponse({'ticket': {
                'id': ticket.id,
                'type': ticket.type,
                'description': ticket.description,
                'status': ticket.status,
                'created_at': ticket.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }})
        except Ticket.DoesNotExist:
            return JsonResponse({'error': 'Ticket no encontrado'}, status=404)
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
##MODELOS DE VISTAS DENTRO DE DJANGO

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  
        else:
            return render(request, 'login.html', {'error': 'Credenciales inválidas'})
    else:
        return render(request, 'login.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Usuario creado con éxito!')  
            return redirect(request.get_full_path())  
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})

@login_required  
def dashboard_view(request):
    user = request.user
    user_type = user.role_id
    return render(request, 'dashboard.html', {'role_id': user_type})

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = CustomUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El perfil se guardo exitosamente!')
            return redirect('profile')  
    else:
        form = CustomUserForm(instance=user)
    return render(request, 'profile.html', {'form': form})

@login_required
def user_administration(request):
    if request.user.role_id != 1:
        return redirect('dashboard')  

    users = CustomUser.objects.all()
    form_status = UserStatusForm()
    form_edit = UserEditForm()
    
    if request.method == 'POST':
        if 'change_status' in request.POST:
            form_status = UserStatusForm(request.POST)
            if form_status.is_valid():
                user_id = form_status.cleaned_data['user_id']
                new_status = form_status.cleaned_data['new_status']
                user = CustomUser.objects.get(id=user_id)
                user.usertype = new_status
                user.save()
                return redirect('user_administration')

        elif 'edit_user' in request.POST:
            form_edit = UserEditForm(request.POST)
            if form_edit.is_valid():
                user_id = form_edit.cleaned_data['user_id']
                new_username = form_edit.cleaned_data['new_username']
                new_email = form_edit.cleaned_data['new_email']
                new_role = form_edit.cleaned_data['new_role']
                user = CustomUser.objects.get(id=user_id)
                user.username = new_username
                user.email = new_email
                user.role_id = new_role
                user.save()
                return redirect('user_administration')

        elif 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(CustomUser, id=user_id)
            user.delete()
            return redirect('user_administration')
            
    return render(request, 'user_administration.html', {'users': users, 'form_status': form_status, 'form_edit': form_edit})

@login_required  
def administrar_productos(request):
    if request.user.role_id == 2:
        return redirect('dashboard') 
    
    form = ProductForm()
    if request.method == 'POST':
        if 'edit_product_id' in request.POST:
            product_id = request.POST.get('edit_product_id')
            product = Product.objects.get(pk=product_id)
            form = ProductForm(request.POST, instance=product)
            if form.is_valid():
                messages.success(request, '¡El producto se edito exitosamente!')
                form.save()
        elif 'delete_product_id' in request.POST:
            product_id = request.POST.get('delete_product_id')
            product = Product.objects.get(pk=product_id)
            product.delete()
            messages.success(request, '¡El producto se borro exitosamente!')
        else:
            form = ProductForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, '¡El producto se añadio exitosamente!')
                return redirect('administrar_productos')

    products = Product.objects.all()
    return render(request, 'administrar_productos.html', {'products': products, 'form': form})

@login_required  
def editar_producto(request, product_id):
    if request.user.role_id == 2:
        return redirect('dashboard') 
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, '¡El producto se edito exitosamente!')
            return redirect('administrar_productos')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'editar_producto.html', {'form': form})

@login_required  
def modificar_stock(request, product_id):
    if request.user.role_id == 2:
        return redirect('dashboard') 
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('administrar_productos')
    else:
        form = StockForm(instance=product)
    return render(request, 'modificar_stock.html', {'form': form})

def get_product_stock(request, product_id):
    try:
        product = Product.objects.get(pk=product_id)
        stock = product.stock
        return JsonResponse({'stock': stock})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'El producto no existe'}, status=404)

@login_required
def inventory_information_dashboard(request):
    products = Product.objects.all()
    inventory_entries = InventoryEntry.objects.all().values('product__name', 'quantity_received', 'date_received')
    inventory_exits = InventoryExit.objects.all().values('product__name', 'quantity_sold', 'date_sold')
    insufficient_stock_products = InsufficientStock.objects.all().values('product__name', 'quantity_needed')
    inventory_entries_list = list(inventory_entries)
    inventory_exits_list = list(inventory_exits)
    insufficient_stock_products_list = list(insufficient_stock_products)
    products_with_insufficient_stock = []
    for product in products:
        stockTotal=0
        for stock in inventory_exits_list:
            if product.name == stock['product__name']:
                stockTotal += stock['quantity_sold']
        profit = stockTotal * product.price
        products_with_insufficient_stock.append({'product_name': product.name,'profit': profit,'quantity_sold': stockTotal,'price': product.price}) 
    data = {
        'inventory_entries': inventory_entries_list,
        'inventory_exits': inventory_exits_list,
        'insufficient_stock_products': insufficient_stock_products_list,
        'products_with_insufficient_stock': products_with_insufficient_stock
    }
    return JsonResponse(data)

@login_required     
def register_inventory_entry(request):
    if request.user.role_id == 2:
        return redirect('dashboard') 
    if request.method == 'POST':
        form = InventoryEntryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La entrada de inventario se registró exitosamente!')
            return render(request, 'register_inventory_entry.html', {'form': InventoryEntryForm()})
    else:
        form = InventoryEntryForm()
    return render(request, 'register_inventory_entry.html', {'form': form})

@login_required  
def register_inventory_exit(request):
    if request.user.role_id == 2:
        return redirect('dashboard') 
    if request.method == 'POST':
        form = InventoryExitForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡La venta se registró exitosamente!')
            return redirect('register_inventory_exit')  
    else:
        form = InventoryExitForm()
    return render(request, 'register_inventory_exit.html', {'form': form})

@login_required 
def inventory_information(request):
    inventory_entries = InventoryEntry.objects.all()
    inventory_exits = InventoryExit.objects.all()
    insufficient_stock_products = InsufficientStock.objects.all()
    return render(request, 'inventory_information.html', {
        'inventory_entries': inventory_entries,
        'inventory_exits': inventory_exits,
        'insufficient_stock_products': insufficient_stock_products
    })

##Componentes para conexion a front y consumo desde otra plataforma

@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def loginapi(request):
    if request.method == 'POST':
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({'email': user.email, 'username': user.username, 'access': str(refresh.access_token)}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
class ProfileEditView(APIView):
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class UserListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if request.user.role_id != 1:
            return Response({"error": "Unauthorized"}, status=403)
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

class UserEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        if request.user.role_id != 1:
            return Response({"error": "Unauthorized"}, status=403)
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
class UserRoleChangeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def put(self, request, pk):
        if not request.user.role_id == 1:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        user = self.get_object(pk)
        new_role_id = request.data.get('role_id', None)
        if new_role_id is None:
            return Response({"error": "Role ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        user.role_id = new_role_id
        user.save()
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)
    
class ProductCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.role_id == 1:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        product = self.get_object(pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.role_id == 1:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        product = self.get_object(pk)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.role_id == 1:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        product = self.get_object(pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class ProductStockAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        product = self.get_object(pk)
        stock = product.stock
        return Response({"stock": stock})
    
class InventoryEntryCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = InventoryEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            product_id = serializer.validated_data['product'].id
            quantity_received = serializer.validated_data['quantity_received']
            product = Product.objects.get(id=product_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryExitCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = InventoryExitSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            product_id = serializer.validated_data['product'].id
            quantity_sold = serializer.validated_data['quantity_sold']
            product = Product.objects.get(id=product_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InventoryEntryListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        entries = InventoryEntry.objects.all()
        serializer = InventoryEntrySerializer(entries, many=True)
        return Response(serializer.data)

class InventoryExitListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        exits = InventoryExit.objects.all()
        serializer = InventoryExitSerializer(exits, many=True)
        return Response(serializer.data)

class InsufficientStockListAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        insufficient_stocks = InsufficientStock.objects.all()
        serializer = InsufficientStockSerializer(insufficient_stocks, many=True)
        return Response(serializer.data)