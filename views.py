from django.views.generic import CreateView, UpdateView, DeleteView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.conf import settings
from .models import Cart
from django.shortcuts import render, redirect
from .models import User
from .forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.shortcuts import reverse
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, HttpBadResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from paypal.standard.forms import PayPalPaymentForm


class CartView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'cart.html'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class AddToCartView(LoginRequiredMixin, CreateView):
    model = Cart
    template_name = 'add_to_cart.html'
    fields = ['product', 'quantity']

    def form_valid(self, form):
        product = form.cleaned_data['product']
        quantity = form.cleaned_data['quantity']
        cart = Cart.objects.create(user=self.request.user, product=product, quantity=quantity)
        return redirect('cart')

class RemoveFromCartView(LoginRequiredMixin, DeleteView):
    model = Cart
    template_name = 'remove_from_cart.html'

    def get_objects(self):
        return Cart.objects.get(id=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        cart = self.get_objects()
        cart.delete()
        return redirect('cart')

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=128)

def register(request):
    if request.method =='POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('Login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))

def home_view(request):
    return render(request, 'home.html', {})


@csrf_exempt
def payment_view(request):
    # Create a PayPalPaymentsForm instance
    paypal_form = PayPalPaymentForm(initial={
        'business': settings.PAYPAL_BUSINESS,
        'item_name': 'My Product',
        'amount': '10.00',
        'currency_code': 'USD',
        'button_source': 'My_Business_Button',
        'notify_url': request.build_absolute_uri(reverse('paypal-ipn')),
    })
    # Render the form
    return render(request, 'payment.html', {'form' : paypal_form})

@csrf_exempt
def paypal_ipn(request):
    # Verify the IPN message
    ipn_message = request.POST.get('ipn_message')
    if not ipn_message:
        return HttpResponseBadRequest('Invalid IPN message')

    # parse the IPN message
    ipn_message = ipn_message.decode('utf-8')
    ipn_message = ipn_message.replace('\\', '')
    ipn_message = ipn_message.replace('"', '')
    ipn_message = ipn_message.replace("'", '')
    ipn_message = ipn_message.replace(' ', '')
    ipn_message = ipn_message.replace('\n', '')
    ipn_message = ipn_message.replace('\r', '')

    # Extract the transaction ID and payment status
    transaction_id = ipn_message.split('&')[0].split('=')[1]
    payment_status = ipn_message.split('&')[1].split('=')[1]

    # Update the payment status in your database
    # ...

    # Return a success response
    return HttpResponse('IPN message processed successfully')