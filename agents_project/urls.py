

from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Usa as views padrão de autenticação Django:
    path('accounts/', include('django.contrib.auth.urls')),

    path('register/', accounts_views.register_view, name='register'),
    path('menu/', accounts_views.menu_view, name='menu'),
    path('', accounts_views.menu_view, name='menu'),
    path('<str:agent_slug>/', accounts_views.agent_chat_view, name='agent_chat'),
]