from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from shop.models import Product
from .models import Cart, CartItem
from .cart import SessionCart

@require_POST
def add_to_cart(request, product_id):
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    set_new_quantity = request.POST.get('update', False)
    if quantity>product.stock:
        messages.error(request, 
                       f"can't add ${quantity} to the cart because ther's ${product.stock} left ")
        return redirect('product_detail',pk=product_id)
    else:
        cart.add(product=product, quantity=quantity, set_new_quantity=set_new_quantity)
    if request.user.is_authenticated:
            sync_cart(request)
    return redirect('cart_detail')

@require_POST
def remove_from_cart(request, product_id):
    cart = SessionCart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


class CartDetailView(View):
    template_name = 'cart/cart_detail.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            cart=sync_cart(request)
            cart= cart.items.all()
        else:
            cart = SessionCart(request)
        return render(request, self.template_name, {'cart': cart})

@login_required
def sync_cart(request):

    session_cart = SessionCart(request)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    for item in session_cart:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=item['product'])
        cart_item.quantity = item['quantity']
        cart_item.save()
    
    session_cart.clear()
    return cart

class CartCountView(View):
    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            cart=sync_cart(request)
            #cart = Cart.objects.get(user=request.user)
            count = cart.items.count()  
            return JsonResponse({'count': count})
        cart = SessionCart(request)          
        return JsonResponse({'count': len(cart)})
        