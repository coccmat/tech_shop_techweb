from django.urls import reverse_lazy
from django.conf import settings
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm
from django.urls import reverse_lazy

from django.contrib.auth import login
from django.contrib.auth.models import Group

# Create your views here.


class SignUpView(CreateView):
    model = settings.AUTH_USER_MODEL
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.save()
        account_type = form.cleaned_data.get('account_type')
        if account_type == 'customer':
            group, _ = Group.objects.get_or_create(name='Customers')
        else:
            group, _ = Group.objects.get_or_create(name='Vendors')
        user.groups.add(group)
        login(self.request, user)
        return super().form_valid(form)

class LoginView(LoginView):
    template_name = 'registration/login.html' 
    def get_success_url(self):
        return reverse_lazy('product_list')
    

    