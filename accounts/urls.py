from django.urls import path, include
from .views import *

urlpatterns = [
    path("login/",LoginView.as_view(), name='login'),
    path("", include("django.contrib.auth.urls")), 
    path('signup/', SignUpView.as_view(), name='signup'),
]



