from django.conf.urls.static import static
from django.urls import path
from django.conf import settings as conf_settings
from bp_shares import settings
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('user-profile', views.user_profile, name='user_profile'),
    path('transaction_history', views.transaction_history, name='txn_history'),
    path('send_bundle/', views.send_bundle_page, name='send_bundle_page'),
    path('login', views.loginpage, name='login'),
    path('sign-up', views.register, name='register'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
] + static(conf_settings.STATIC_URL, document_root=conf_settings.STATIC_ROOT)


