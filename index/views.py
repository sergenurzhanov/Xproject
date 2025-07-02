from django.shortcuts import render, redirect
from .models import Product, Category, Cart
from .forms import RegForm
from django.views import View
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
import telebot

# Cоздаем объект бота
bot = telebot.TeleBot('8189429025:AAE6NsBE9l-mgPeH_cu1NUHRaP0-T6DXkx8')



# Create your views here.
def home_page(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'home.html', context)


# Страница выбранной категории
def category_page(request, pk):
    category = Category.objects.get(id=pk)
    products = Product.objects.filter(product_category=category)

    #Отправляем данные на фронт
    context = {
        'category': category,
        'products': products
    }
    return render(request, 'category.html', context)

# Страница выбранного товара
def product_page(request, pk):
    product = Product.objects.get(id=pk)

    context = {'product': product}
    return render(request, 'product.html', context)

# Поиск товара
def search(request):
    if request.method == 'POST':
        get_product = request.POST.get('search_product')
        searched_product = Product.objects.filter(product_name__iregex=get_product)

        if searched_product:
            context = {
                'products': searched_product,
                'request': get_product
            }
            return render(request, 'result.html', context)
        else:
            context = {
                'products': '',
                'request': get_product
            }
            return render(request, 'result.html', context)

# Регистрация
class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {'form': RegForm}
        return render(request, self.template_name, context)

    def post(self, request):
        form = RegForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password2')

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            login(request, user)
            return redirect('/')
# выход из акк
def logout_view(request):
    logout(request)
    return redirect('/')

# Добавление товара в корзину
def add_to_cart(request, pk):
    if request.method == 'POST':
        product = Product.objects.get(id=pk)

        if 1 <= int(request.POST.get('product_count')) <= product.product_count :
            Cart.objects.create(user_id=request.user.id, user_product=product, user_pr_amount=int(request.POST.get('product_count'))).save()
            return redirect('/')
        return redirect(f'/product/{pk}')

# Удаление товара из корзины
def del_from_cart(request, pk):
    product_to_del = Product.objects.get(id=pk)
    Cart.objects.filter(user_product=product_to_del).delect()

    return redirect('/cart')


# Отображение корзины
def show_cart(request):
    user_cart = Cart.objects.filter(user_id=request.user.id)
    totals = [round(t.user_product.product_price * t.user_pr_amount) for t in user_cart]

    context = {
        'cart': user_cart,
        'total': round(sum(totals), 2)
    }

    if request.method == 'POST':
        text = (f'Новый заказ!/\n'
                f'Клиент: {User.objects.get(id=request.user.id).email}\n\n')

        for i in user_cart:
            product = Product.objects.get(id=i.user_product.id)
            product.product_count = product.product_count - i.user_pr_amount
            product.save(update_fields=['product_count'])

            text += (f'Товар: {i.user_product}\n'
                     f'Количество: {i.user_pr_amount}\n'
                     f'----------------------------------\n')
        text += f'Итого: ${round(sum(totals, 2))}'
        bot.send_message(643869009, text)
        user_cart.delete()
        return redirect('/')
    return render(request, 'cart.html', context)