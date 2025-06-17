from django.contrib import admin
from django.urls import path
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('menu/', accounts_views.menu_view, name='menu'),
    path('login/', accounts_views.login_view, name='login'),
    path('register/', accounts_views.register_view, name='register'),
    path('forgot-password/', accounts_views.forgot_password_view, name='forgot_password'),
    path('', accounts_views.menu_view, name='menu'),
    path('<str:agent_slug>/', accounts_views.agent_chat_view, name='agent_chat'),
]