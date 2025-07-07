from django.contrib import admin
from .models import *

class BrandAdmin(admin.ModelAdmin):
    list_display=('BrandId','BrandName')

#class StockAdmin(admin.ModelAdmin):
#   list_display=('StockId','BrandId','Date','Count','PurchasePrice','TotalPurchasedPrice','AssignedPrice','TotalAssignedPrice')

# Register your models here.
admin.site.register(Brand,BrandAdmin)
admin.site.register(Stock)
admin.site.register(Sell)
admin.site.register(PresentStock)
admin.site.register(Lens)
    