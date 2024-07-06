from django.db import IntegrityError
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q,F, Count, Sum
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from .signals import sale_confirmation
from .models import NotificationRequest
from cart.views import sync_cart
from .models import *
from .forms import ProductForm, ReviewForm, SearchForm
from .enum import CategoryEnum, StatusEnum




class GroupRequiredMixin(UserPassesTestMixin):
    group_required = None

    def test_func(self):
        if self.group_required is None:
            raise PermissionDenied("You must specify 'group_required'.")

        if isinstance(self.group_required, str):
            groups = [self.group_required]
        else:
            groups = self.group_required

        return self.request.user.groups.filter(name__in=groups).exists()

    def handle_no_permission(self):
        return super().handle_no_permission()

def product_list(request):
    category = request.GET.get('category')
    sort = request.GET.get('sort', 'name')
    
    products = (Product.objects
                           .annotate(total_sales=Sum(F('orderitem__quantity')))
                           .order_by('-total_sales'))
    if category:
        products = products.filter(category=category)

    if sort:
        products = products.order_by(sort)

    paginator = Paginator(products, 9)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        most_purchased_category = (OrderItem.objects
                                    .filter(order__user=request.user)
                                    .values('product__category')
                                    .annotate(total=Count('product__category'))
                                    .order_by('-total')
                                    .first())
        
        if most_purchased_category:
            category = most_purchased_category['product__category']
            for_you_products = (Product.objects
                                .filter(category=category)
                                .annotate(total_sold=Sum(F('orderitem__quantity')))
                                .order_by('-total_sold')[:10])
        else:
            for_you_products = Product.objects.none()
    else:
        for_you_products = Product.objects.none()

    context = {
        'products': page_obj,
        'categories': [cat for cat in CategoryEnum],
        'for_you_products': for_you_products,
    }
    return render(request, 'shop/product_list.html', context)


class ProductDetailView(View):
        def get(self, request, pk):
            product = get_object_or_404(Product, pk=pk)
            related_products = (Product.objects
                                .filter(category=product.category)
                                .exclude(pk=pk)
                                .annotate(total_sold=Sum(F('orderitem__quantity')))
                                .order_by('-total_sold')[:4])

            reviews = product.reviews.all()

            if (self.request.user.is_authenticated 
                    and OrderItem.objects.filter(status=StatusEnum.CONFIRMED,
                                                 product=product, 
                                                 order__user=self.request.user)):
                review_form =  ReviewForm()
            else:
                review_form= None
            from django.db.models import Avg
            average_rating=Review.objects.filter(product=product).aggregate(average_rate=Avg("rating", default=0))
            context={
                'product': product,
                'related_products': related_products,
                'reviews': reviews,
                'review_form': review_form,
                'average' : average_rating['average_rate'],
            }
            return render(request, 'shop/product_detail.html', context)
        def post(self, request, pk):
            product = get_object_or_404(Product, pk=pk)
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.product = product
                review.customer = self.request.user
                review.save()
                return redirect('product_detail', pk=pk)
            related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
            reviews = product.reviews.all()
            if OrderItem.objects.filter(status=StatusEnum.CONFIRMED,product=product, order__user=self.request.user):
                review_form =  ReviewForm()
            else:
                review_form= None
            return render(request, 'shop/product_detail.html', {
                'product': product,
                'related_products': related_products,
                'reviews': reviews,
                'review_form': form,
            })

        
class AddReviewView(GroupRequiredMixin,CreateView):
    model = Review
    form_class = ReviewForm
    group_required='Customers'

    template_name = 'shop/add_review.html'

    def form_valid(self, form):
        form.instance.product = get_object_or_404(Product, pk=self.kwargs['pk'])
        form.instance.customer = self.request.user
        return super().form_valid(form)
    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.kwargs['pk']})


class VendorSaleDashboardView(GroupRequiredMixin,ListView):
    model=Product
    template_name = 'shop/graphs.html'
    group_required='Vendors'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Product.objects.filter(vendor=self.request.user).order_by("name")
        labels = [product.name for product in products]
        data = [Sale.objects.filter(sold_item__product=product)
                .aggregate(total_quantity=Sum(F('sold_item__quantity')))['total_quantity'] or 0
                for product in products]
        request_data = [NotificationRequest.objects.filter(product=product).count() for product in products]
        print(data)
        
        context['labels'] = labels
        context['data'] = data
        context['request_data'] = request_data
        return context

class VendorDashboardView(GroupRequiredMixin,ListView):
    model=Product
    template_name = 'shop/vendor_dashboard.html'
    group_required='Vendors'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products']=Product.objects.filter(vendor=self.request.user).order_by("name")
        return context
    
class ManageProductView(GroupRequiredMixin,UpdateView):
    model = Product
    group_required='Vendors'
    form_class = ProductForm
    template_name = 'shop/manage_product.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        
        return Product.objects.filter(vendor=self.request.user)

    def get_success_url(self):
        return reverse_lazy('vendor_dashboard')


class AddProductView(GroupRequiredMixin,CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/add_product.html'
    group_required='Vendors'

    def form_valid(self, form):
        form.instance.vendor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('vendor_dashboard')


class RequestNotification(GroupRequiredMixin,View):
    group_required='Customers','Vendors'
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, id=pk)

        try:
            NotificationRequest.objects.create(product=product, user=request.user)
            messages.success(request, 'You have successfully requested a notification for this product.')
        except IntegrityError:
            messages.error(request, 'You have already requested a notification for this product.')

        return redirect('product_detail', pk=pk)

class NotificationListView(ListView):
    model = NotificationRequest
    template_name = 'shop/notification_list.html'
    context_object_name = 'notifications'
    def get_queryset(self):
        filter = {'back_in_stock': True, 'user': self.request.user}
        return NotificationRequest.objects.filter(**filter).order_by("requested_at")


@login_required
def create_order(request):
    
    'Sync the session cart with the database cart'
    cart = sync_cart(request)   
    if len(cart.items.all()) == 0:
        return redirect('cart_detail')

    order = Order.objects.create(user=request.user)
    for cart_item in cart.items.all():
        product = cart_item.product
        quantity = cart_item.quantity
        if product.stock < quantity:
            messages.error(request, f"You have tried to order {quantity} but there's only {product.stock} in stock")
            return redirect('product_detail', pk=product.id)        
        else:     
            product.stock -= quantity
            product.save()

        # Create the actual order item
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            status=StatusEnum.PENDING
        )

    cart.items.all().delete()  
    messages.success(request, 'Your order has been created successfully!')
    return redirect('order_detail', order_id=order.id)

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'shop/order_detail.html', {'order': order})

@method_decorator(login_required, name='dispatch')
class OrderListView(ListView):
    model = Order
    template_name = 'shop/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10  

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    

class SearchResultsView(View):
    template_name = 'shop/search_results.html'

    def get(self, request):
        form = SearchForm(request.GET)
        query = request.GET.get('query')
        results = []

        if query:
            results = Product.objects.filter(
                Q(name__icontains=query) 
                | Q(description__icontains=query) 
                | Q(category__icontains=query) 
                ).distinct()
        context={'form': form, 
                 'query': query, 
                 'results': results}

        return render(request, self.template_name, context)

@login_required
def unread_notification_count(request):
    unread_count = NotificationRequest.objects.filter(user=request.user, 
                                                      read=False,
                                                      back_in_stock=True).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(NotificationRequest, 
                                     id=notification_id, 
                                     user=request.user)
    notification.read = True
    notification.save()
    return redirect('notification_list')

@login_required
def delete_read_notifications(request):
    read_notifications = NotificationRequest.objects.filter(user=request.user,
                                                            read=True)
    read_notifications.delete()
    read_notifications.update()
    return JsonResponse({'read_notifications': read_notifications.count()})


class SalesListView(GroupRequiredMixin,ListView):
    model = OrderItem
    template_name = 'shop/sales_list.html'
    context_object_name = 'orders'
    group_required='Vendors'
    ordering = ['-created_at']

    def get_queryset(self):
        return OrderItem.objects.filter(product__vendor=self.request.user)
        

class ConfirmOrderView(GroupRequiredMixin,View):
    group_required='Vendors'
    def post(self, request,item_id):
        item = get_object_or_404(OrderItem, id=item_id)
        if item.status != StatusEnum.CONFIRMED:
            item.status = StatusEnum.CONFIRMED
            item.save()
            sale_confirmation.send(sender=OrderItem, instance=item, vendor=self.request.user)
        return redirect('sales_list')