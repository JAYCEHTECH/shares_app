from django.conf.urls.static import static
from django.urls import path
from django.conf import settings as conf_settings
from bp_shares import settings
from . import views
from django.contrib.auth.views import LogoutView
from .api import api_views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('', views.home, name='home'),
    path('user-profile', views.user_profile, name='user_profile'),
    path('transaction_history', views.transaction_history, name='txn_history'),
    path('send_bundle/', views.send_bundle_page, name='send_bundle_page'),
    path('login/', views.loginpage, name='login'),
    path('sign-up', views.register, name='register'),
    path("api-mgt", views.api_page, name="api_mgt"),
    path("crediting/", views.crediting_page, name="crediting"),
    path("credit-history/", views.credit_history, name="credit-history"),
    path("query_transaction/", views.query_transaction, name="query_transaction"),
    path("all_transactions/", views.all_transactions, name="all_transactions"),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path("fix_txn/<str:ref>", views.fix_transaction, name='fix_transaction'),

    # =================== API URLS ===============================
    path('api_keys/', api_views.APIKeysView.as_view(), name='api-keys'),
    path('validate-api-keys/', api_views.ValidateAPIKeysView.as_view(), name='validate-api-keys'),
    path("api-token-auth/", obtain_auth_token),
    path("api/user_bundle_volume", api_views.user_balance, name='user_balance'),
    path("api/flexi/v1/transactions/", api_views.transactions, name="transactions"),
    path("api/flexi/v1/all_transactions/", api_views.get_all_transactions, name="all_user_transactions"),
    path("api/flexi/v1/new_transaction/", api_views.NewTransactionView.as_view(), name="new_transaction"),
    path("api/flexi/v1/transaction_detail/<str:reference>/", api_views.TransactionDetail.as_view(), name='transaction_detail'),
    path("api/flexi/v1/transaction_detail/", api_views.null_transaction_query, name='null_transaction'),
] + static(conf_settings.STATIC_URL, document_root=conf_settings.STATIC_ROOT)


