from django.urls import path
from . import views
from django.contrib.auth.views import  LoginView


urlpatterns = [
    path('',views.signin),
    path('home/', views.home,name="home"),
    path('brand/',views.brand),
    path('stock/',views.stock,name='stock'),
    path('sell/',views.sell),
    path('summary/',views.summary),
    path('ShippingVendor/',views.shippingVendor),
    path('glassFitting/',views.GlassFitting),
    path('brand/brandSummary/',views.brandSummary),
    path('summary/sellSummary/',views.sellSummary),
    path('summary/PrescriptionSummary/',views.PrescriptionSummary),
    path('summary/ExpenditureSummary/',views.expenditureSummary),
    path('summary/download_Sell/',views.download_Sell),
    path('summary/download_Stock/',views.download_Stock),

]