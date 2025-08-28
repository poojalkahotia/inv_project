# invapp/urls.py

from django.urls import path

# Import views from separate files inside the views package

from invapp.views.party_views import  party_view,  party_delete
from invapp.views.category_views import category_view
from invapp.views.item_views import item_view,  item_delete
from invapp.views.dashboard_views import dashboard
from invapp.views.company_views import company_view
from invapp.views import purchase_views,sale_views,rec_views,pay_views
from invapp.reports import report_views 
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
urlpatterns = [
    # Dashboard
    path("dashboard/", dashboard, name='dashboard'),

    # Company URLs
    path('companies/', company_view, name='company'),

    # Party URLs
    path('parties/', party_view, name='party'),
    path('parties/edit/<str:pk>/', party_view, name='party_edit'),
    path('parties/delete/<str:pk>/', party_delete, name='party_delete'),
    # Category URLs
    path('categories/', category_view, name='category'),
    
    # Item URLs
    path('items/', item_view, name='item'),
    path('items/edit/<str:pk>/', item_view, name='item_edit'),
    path('items/delete/<str:pk>/', item_delete, name='item_delete'),

    path('purchase/', purchase_views.purchase_form, name='purchase_form_new'),
    path('purchase/<int:invno>/', purchase_views.purchase_form, name='purchase_form_update'),
    path('purchase/save/', purchase_views.save_purchase, name='save_purchase'),
    path('purchase/update/<int:invno>/', purchase_views.update_purchase, name='update_purchase'),
    path('purchase/delete/<int:invno>/', purchase_views.delete_purchase, name='delete_purchase'),
    path('purchasedata/', purchase_views.purchase_data_view, name='purchasedata'),
    
    path('num-to-words/', purchase_views.num_to_words, name='num_to_words'),
    
    path('sale/', sale_views.sale_form, name='sale_form_new'),
    path('sale/<int:invno>/', sale_views.sale_form, name='sale_form_update'),
    path('sale/save/', sale_views.save_sale, name='save_sale'),
    path('sale/update/<int:invno>/', sale_views.update_sale, name='update_sale'),
    path('sale/delete/<int:invno>/', sale_views.delete_sale, name='delete_sale'),
    path('saledata/', sale_views.sale_data_view, name='saledata'),
    

    
    # Payment URLs
    path('pay/', pay_views.payment_view, name='pay'),
    path('paydata/', pay_views.paydata, name='paydata'),
    #path('paylist/', pay_list, name='pay_list'),
    
    path('pay/update/<int:entryno>/', pay_views.update_payment, name='update_payment'),
    path('pay/delete/<int:entryno>/', pay_views.delete_payment, name='delete_payment'),

    # Receipt URLs
    path('rec/', rec_views.rec, name='rec'),
    path('recdata/', rec_views.recdata, name='recdata'),
    #path('reclist/', rec_list, name='rec_list'),
    path('rec/update/<int:entryno>/', rec_views.update_rec, name='update_rec'),
    
    path('delete_rec/<int:entryno>/', rec_views.delete_rec, name='delete_rec'),
    
    #reports
    path("allpartybalance/",report_views.all_party_balance, name="all_party_balance"),
    path('party-st/', report_views.party_st, name='party-st'),
    path("all-item-balance/", report_views.all_item_balance, name="all_item_balance"),
    path('item-statement/', report_views.item_st, name='item_statement'),
    path('purchase-report/', report_views.purmaster_report, name='purmaster_report'),
    path('sales-report/', report_views.salemaster_report, name='salemaster_report'),
    path('receipt-report/', report_views.recmaster_report, name='recmaster_report'),
    path('payment-report/', report_views.paymaster_report, name='paymaster_report'),
    
    #reports
    
    path("allpartybalance/pdf/", report_views.all_party_balance_pdf, name="all_party_balance_pdf"),
    path("all-item-balance/pdf/", report_views.all_item_balance_pdf, name="all_item_balance_pdf"),
    path("partyst/pdf/<str:partyname>/", report_views.party_st_pdf, name="party_st_pdf"),
    path("purchase_report/pdf/", report_views.purchase_report_pdf, name="purchase_report_pdf"),
    path("sale/<str:invno>/pdf/", report_views.sale_pdf, name="sale_pdf"),
    path('receipt_report/pdf/', report_views.receipt_report_pdf, name='receipt_report_pdf'),
    path('payment_report/pdf/', report_views.payment_report_pdf, name='payment_report_pdf'),

    # Authentication URLs
    path("login/", auth_views.LoginView.as_view(template_name="auth/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password_change/",login_required (auth_views.PasswordChangeView.as_view(template_name="auth/password_change.html", success_url=reverse_lazy('password_change_done'))), name="password_change"),
    path("password_change/done/",login_required (auth_views.PasswordChangeDoneView.as_view(template_name="auth/password_change_done.html")), name="password_change_done"),

    # Root URL redirects to login page
    path("", auth_views.LoginView.as_view(template_name="auth/login.html")),




]
