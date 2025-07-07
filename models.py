from django.db import models

# Create your models here.
class Brand(models.Model):
    BrandId=models.AutoField(primary_key=True)
    BrandName=models.CharField(max_length=255)

class Stock(models.Model):
    StockId=models.AutoField(primary_key=True)
    BrandId=models.IntegerField(null=True)
    Date=models.DateField(null=True)
    Count=models.IntegerField(null=True)
    PurchasePrice=models.FloatField(null=True)
    TotalPurchasedPrice=models.FloatField(null=True)
    AssignedPrice=models.FloatField(null=True)
    TotalAssignedPrice=models.FloatField(null=True)
    PresentCount=models.IntegerField(null=True)

class Sell(models.Model):
    SellId=models.AutoField(primary_key=True)
    BrandId=models.IntegerField(null=True)
    SellingPrice=models.FloatField(null=True)
    FramePrice=models.FloatField(null=True)
    AdvanceAmount=models.FloatField(null=True)
    RemainingAmount=models.FloatField(null=True)
    SoldToName=models.CharField(max_length=500,null=True)
    SoldOnDate=models.DateField(null=True)
    FullPaymentDone=models.BooleanField(null=True)
    FullPaymentDate=models.DateField(null=True)
    LensType=models.CharField(max_length=500,null=True)
    LensPrice=models.FloatField(null=True)
    DiscountPercent=models.FloatField(null=True)
    PaymentMode=models.CharField(max_length=500,null=True)
    RemainingAmtPaymentMode=models.CharField(max_length=500,null=True)
    IsShipped=models.BooleanField(null=True)
    IsFittingPaid=models.BooleanField(null=True)

class PresentStock(models.Model):
    Id=models.AutoField(primary_key=True)
    StockId=models.IntegerField(null=True)
    BrandId=models.IntegerField(null=True)
    #BrandId=models.ForeignKey(Brand, related_name='PresentStock', on_delete=models.CASCADE)
    OriginalCount=models.IntegerField(null=True)
    PresentCount=models.IntegerField(null=True)
    UpdatedOnDate=models.DateField(null=True)

class Lens(models.Model):
    LensId=models.AutoField(primary_key=True)
    LensName=models.CharField(max_length=255)
    LensMinCost=models.FloatField(null=True)

class Prescription(models.Model):
    PrescriptionId=models.AutoField(primary_key=True)
    Sellid=models.IntegerField()
    Date=models.DateField(null=True)
    distSphericalR=models.CharField(max_length=255,null=True,blank=True)
    distCylindricalR=models.CharField(max_length=255,null=True,blank=True)
    distAxisR=models.CharField(max_length=255,null=True,blank=True)
    distVisionR=models.CharField(max_length=255,null=True,blank=True)
    AddSphericalR=models.CharField(max_length=255,null=True,blank=True)
    AddCylindricalR=models.CharField(max_length=255,null=True,blank=True)
    AddAxisR=models.CharField(max_length=255,null=True,blank=True)
    AddVisionR=models.CharField(max_length=255,null=True,blank=True)
    distSphericalL=models.CharField(max_length=255,null=True,blank=True)
    distCylindricalL=models.CharField(max_length=255,null=True,blank=True)
    distAxisL=models.CharField(max_length=255,null=True,blank=True)
    distVisionL=models.CharField(max_length=255,null=True,blank=True)
    AddSphericalL=models.CharField(max_length=255,null=True,blank=True)
    AddCylindricalL=models.CharField(max_length=255,null=True,blank=True)
    AddAxisL=models.CharField(max_length=255,null=True,blank=True)
    AddVisionL=models.CharField(max_length=255,null=True,blank=True)
    TypeOfGlass=models.CharField(max_length=255,null=True,blank=True)

  

class ShippingVendor(models.Model):
    ShippingVendorId=models.AutoField(primary_key=True)
    Sellid=models.IntegerField()
    SentOnDate=models.DateField(null=True)
    ShippingAmount=models.FloatField(null=True,blank=True)
  
    
class GlassFittingVendor(models.Model):
    GlassFittingVendorId=models.AutoField(primary_key=True)
    Sellid=models.IntegerField()
    EnteredOnDate=models.DateField(null=True)
    LensCost=models.FloatField(null=True,blank=True)
    FittingCost=models.FloatField(null=True,blank=True)
    TotalCost=models.FloatField(null=True,blank=True)
  

class Expenditure(models.Model):
    ExpenditureId=models.AutoField(primary_key=True)
    Sellid=models.IntegerField()
    SoldOnDate=models.DateField(null=True)
    SoldToName=models.CharField(max_length=255,null=True)
    SentOnDate=models.DateField(null=True)
    FramePrice=models.FloatField(null=True)
    LensPrice=models.FloatField(null=True)
    SellingPrice=models.FloatField(null=True)
    FramePurchasePrice=models.FloatField(null=True,blank=True)
    ShippingAmount=models.FloatField(null=True,blank=True)
    LensCost=models.FloatField(null=True,blank=True)
    FittingCost=models.FloatField(null=True,blank=True)
    TotalCost=models.FloatField(null=True,blank=True)



