from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Brand, Stock,Sell,PresentStock,Lens,Prescription,GlassFittingVendor,ShippingVendor,Expenditure
from django.core import serializers
from datetime import date,datetime
from django.contrib import messages
import csv,io
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.db import connection
from django.db.models import Sum
from django.db.models.functions import TruncDate

# Create your views here.
def home(request):
    '''
    #for Best selling brand of the month
    BSB=Sell.objects.raw('Select s.StockId, b.BrandName,(s.count-s.PresentCount) as maxsell from optical_stock s join optical_brand b On b.BrandId=s.BrandId \
                         join optical_sell se on b.BrandId=se.BrandId where strftime(\'%m\', date(\'now\')) =strftime(\'%m\', se.SoldOnDate) \
                            order by 3 DESC LIMIT 1;')
                            '''
    #for displaying pending payments
    Psell=Sell.objects.filter(FullPaymentDone=False)
    if request.method == "POST": 
        print("Inside")
        sellid=request.POST.get('clear')
        print("Sellid",sellid)
        Pmode=request.POST.get(str(sellid)) 
        print("Pmode",Pmode)
        Sell.objects.filter(SellId=sellid).update(FullPaymentDone="True",FullPaymentDate=datetime.now(),RemainingAmtPaymentMode=Pmode)
        return  HttpResponseRedirect("/home")
    else:
        messages.info(request, '') 
    return render(request,'Home.html',{'Psell':Psell}) 

def signin(request):
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(username=username,password=password)

        if user is not None:
            print("in if")
            login(request,user)
            Psell=Sell.objects.filter(FullPaymentDone=False)
            fname=user.first_name
            return render(request, "Home.html",{'fname':fname,'Psell':Psell})
        else:
            print("in else")
            messages.error(request,"Invalid Credentials")
            return redirect('home')
 
    return render(request, "login.html") 


        
def brand(request):
    b=Brand()
    b.BrandName=request.POST.get('BrandName')
    if request.method == "POST": 
        if Brand.objects.filter(BrandName__iexact=b.BrandName).count()==0:
            b.save()
            messages.info(request, 'Brand record saved successfully!')   
        else:
            messages.info(request, 'Brand already exists!')  
    return render(request,'Brands.html')  

def stock(request):
    displayBrands=Brand.objects.all().order_by('BrandName')
    s=Stock()
    s.BrandId=request.POST.get('Fbrand')
    s.Date=date.today()
    s.Count=request.POST.get('FrameCount')
    s.PresentCount=request.POST.get('FrameCount')
    s.PurchasePrice=request.POST.get('PurchasePrice')
    s.TotalPurchasedPrice= int(s.Count or 0)*int(s.PurchasePrice or 0) 
    s.AssignedPrice=request.POST.get('AssignedPrice')
    s.TotalAssignedPrice=int(s.Count or 0)*int(s.AssignedPrice or 0)
    #print(s.BrandId,s.Count,s.PurchasePrice,s.TotalPurchasedPrice,s.AssignedPrice,s.TotalAssignedPrice)     
    if request.method == "POST": 
         s.save()
         messages.info(request, 'Stock record saved successfully!')
         #Add it to PresentStock after addition    
         PresentStock.objects.create(StockId=s.StockId, BrandId=s.BrandId, OriginalCount=s.Count,PresentCount=s.Count,UpdatedOnDate=datetime.now())  
         return  HttpResponseRedirect("/stock")
    return render(request,'Stock.html',{"Brand":displayBrands})  

def sell(request):
    
    #displayBrands=Brand.objects.all().order_by('BrandName')
    #displayBrands = Brand.objects.select_related('PresentStock').filter(PresentCount__gte=0)
    #displayBrands = Brand.objects.prefetch_related(Prefetch('BrandId', queryset=PresentStock.objects.filter(PresentCount__gte=0)))
    #displayBrands = Brand.objects.filter(PresentStock__PresentCount__gt=0).distinct()
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT DISTINCT b.BrandId, b.BrandName
            FROM optical_brand b
            JOIN optical_stock s ON b.BrandId = s.BrandId
            WHERE s.PresentCount > 0
        """)
        rows = cursor.fetchall()

    # Create Brand objects from raw SQL query results
    brands_with_stock = []
    for row in rows:
        brand_id, brand_name = row
        brand = {
            'BrandId': brand_id,
            'BrandName': brand_name,
        }
        brands_with_stock.append(brand)




    displayLens=Lens.objects.all()
    stocks2 = serializers.serialize("json", Stock.objects.all())
    se=Sell()
    se.BrandId=request.POST.get('Fbrand')
    se.FramePrice=request.POST.get('AssignedFramePrice')
    print("Frame price",se.FramePrice)
    print("Selling Price",request.POST.get('SellingPrice'))
    se.SellingPrice=request.POST.get('SellingPrice')
    se.AdvanceAmount=request.POST.get('AdvancePrice')
    se.RemainingAmount=float(se.SellingPrice or 0)- float(se.AdvanceAmount or 0)
    se.RemainingAmount=round(se.RemainingAmount,2)
    se.SoldToName=request.POST.get('SoldTo')
    se.SoldOnDate=request.POST.get('SoldOnDate') or datetime.now()
    se.IsShipped=False
    se.IsFittingPaid=False
    if se.RemainingAmount==0:
        se.FullPaymentDone=True
    else:
        se.FullPaymentDone=False
    se.LensType=request.POST.get('Lname')
    print(se.LensType)
    se.LensPrice=request.POST.get('LensPrice')
    se.DiscountPercent=request.POST.get('DiscountGiven')
    se.PaymentMode=request.POST.get('PMode')

    ps=Prescription()
    
    ps.distSphericalR=request.POST.get('distSphR') or None
    ps.distCylindricalR=request.POST.get('distCylR')or None
    ps.distAxisR=request.POST.get('distAxisR')or None
    ps.distVisionR=request.POST.get('distVnR')or None
    ps.AddSphericalR=request.POST.get('AddSphR')or None
    ps.AddCylindricalR=request.POST.get('AddCylR')or None
    ps.AddAxisR=request.POST.get('AddAxisR')or None
    ps.AddVisionR=request.POST.get('AddVnR')or None
    ps.distSphericalL=request.POST.get('distSphL')or None
    ps.distCylindricalL=request.POST.get('distCylL')or None
    ps.distAxisL=request.POST.get('distAxisL')or None
    ps.distVisionL=request.POST.get('distVnL')or None
    ps.AddSphericalL=request.POST.get('AddSphL')or None
    ps.AddCylindricalL=request.POST.get('AddCylL')or None
    ps.AddAxisL=request.POST.get('AddAxisL')or None
    ps.AddVisionL=request.POST.get('AddVnL')or None
    ps.TypeOfGlass=request.POST.get('TypeofGlass')or None


    print(se.BrandId,se.SellingPrice,se.AdvanceAmount,se.RemainingAmount,se.SoldToName,se.SoldOnDate)   
    if request.method == "POST":
        criterion1 = Q(BrandId=se.BrandId)
        criterion2 = Q(PresentCount__gt=0)
        print(Stock.objects.filter(criterion1 & criterion2).exists())
        if(Stock.objects.filter(criterion1 & criterion2).exists()): 
            se.save()
            messages.info(request, 'Selling record saved successfully!')  
            #update stock with one less for the same brand Id se.BrandId in PresentStock
            #print(se.BrandId)
            stock=Stock.objects.get(BrandId=se.BrandId)
            #print(stock.StockId,stock.BrandId,stock.Count,stock.PresentCount)
            PresentStock.objects.create(StockId=stock.StockId, BrandId=stock.BrandId, OriginalCount=stock.Count,PresentCount=stock.PresentCount-1,UpdatedOnDate=datetime.now())
            #update present count to -1 in Stock
            stock1 = Stock.objects.get(BrandId=se.BrandId)
            stock1.PresentCount =stock.PresentCount-1 
            stock1.save()
            #update prescription table with prescription
            #sold=Sell.objects.get(SoldToName=se.SoldToName)
            sold=Sell.objects.filter(SoldToName=se.SoldToName,BrandId=se.BrandId,SellingPrice=se.SellingPrice,SoldOnDate=se.SoldOnDate).first()
            soldid=sold.pk
            ps.Sellid=soldid
            ps.Date=datetime.now()
            ps.save()

            return  HttpResponseRedirect("/sell")
        else:
            messages.info(request, 'No such stock exists or Stock empty. Please recheck the brand.')  

    return render(request,'Sell.html',{"Brand":brands_with_stock,"stocks2":stocks2,"Lens":displayLens})  

#For STock
def summary(request):
    FromDate=request.POST.get('FromDate')
    ToDate=request.POST.get('ToDate')
    BrandName=request.POST.get('BrandName') 
    PresentC=request.POST.get('PresentCount')
    if (FromDate !=None or ToDate !=None or BrandName !=None) or PresentC==1:
        Allstock=Stock.objects.raw('Select s.StockId,b.BrandName,s.Date,s.Count,s.PresentCount,s.PurchasePrice,s.AssignedPrice,s.TotalPurchasedPrice,s.TotalPurchasedPrice from optical_stock s \
                               join optical_brand b on b. BrandId=s.BrandId where (s.Date >= %s and s.Date<=%s) or (b.BrandName =%s) or (s.PresentCount>0)',[FromDate,ToDate,BrandName])
    else:
        Allstock=Stock.objects.raw('Select s.StockId,b.BrandName,s.Date,s.Count,s.PresentCount,s.PurchasePrice,s.AssignedPrice,s.TotalPurchasedPrice,s.TotalPurchasedPrice from optical_stock s \
                               join optical_brand b on b. BrandId=s.BrandId') 
    if request.POST.get("clear"):
        print("in clear")
        Allstock=Stock.objects.raw('Select s.StockId,b.BrandName,s.Date,s.Count,s.PresentCount,s.PurchasePrice,s.AssignedPrice,s.TotalPurchasedPrice,s.TotalPurchasedPrice from optical_stock s \
                               join optical_brand b on b. BrandId=s.BrandId') 
    return render(request,'Summary.html',{"Allstock":Allstock})  


    
def brandSummary(request):
    brand =Brand.objects.all().order_by('BrandName')
    return render(request,'BrandSummary.html', {'brand':brand}) 

def sellSummary(request):
    FromDate=request.POST.get('FromDate')
    ToDate=request.POST.get('ToDate')
    BrandName=request.POST.get('BrandName')
    Fullpayment=request.POST.get('FullPayment')
  
    if FromDate !=None or ToDate !=None or BrandName !=None or Fullpayment==1 :
        AllSell=Sell.objects.raw('Select s.SellId,b.BrandName,s.SoldOnDate,s.SoldToName,s.FramePrice,s.LensPrice, s.SellingPrice,s.DiscountPercent,\
        s.LensType ,s.AdvanceAmount,s.PaymentMode,s.RemainingAmount,s.FullPaymentDone,s.FullPaymentDate,\
        s.RemainingAmtPaymentMode from optical_sell s\
        join optical_brand b on s.BrandId=b.BrandId where (s.SoldOnDate >= %s and s.SoldOnDate<=%s) or (b.BrandName =%s) or s.FullPaymentDone=False',[FromDate,ToDate,BrandName])
    else:
        AllSell=Sell.objects.raw('Select s.SellId,b.BrandName,s.SoldOnDate,s.SoldToName,s.FramePrice,s.LensPrice, s.SellingPrice,s.DiscountPercent,\
        s.LensType ,s.AdvanceAmount,s.PaymentMode,s.RemainingAmount,s.FullPaymentDone,s.FullPaymentDate,\
        s.RemainingAmtPaymentMode from optical_sell s join optical_brand b on s.BrandId=b.BrandId') 
    if request.POST.get("clear"):
        AllSell=Sell.objects.raw('Select s.SellId,b.BrandName,s.SoldOnDate,s.SoldToName,s.FramePrice,s.LensPrice, s.SellingPrice,s.DiscountPercent,\
        s.LensType ,s.AdvanceAmount,s.PaymentMode,s.RemainingAmount,s.FullPaymentDone,s.FullPaymentDate,\
        s.RemainingAmtPaymentMode from optical_sell s  join optical_brand b on s.BrandId=b.BrandId')

    return render(request,'SellSummary.html',{'AllSell':AllSell}) 


def download_Sell(request):
    Sells=Sell.objects.all()

    responce=HttpResponse(content_type="text/csv")
    responce['Content-Disposition']='attachment; filename=SellSummary.csv'+str(datetime.now())+'.csv'
    writer=csv.writer(responce, delimiter=','  )
    writer.writerow(['SellId','SoldOnDate','SoldToName','BrandId','BrandName','FramePrice','LensPrice','TotalSellingPrice','DiscountPercentage','AdvanceAmount','PaymentMode',\
                     'RemainingAmount','FullPaymentDone','FullPaymentDate','RemainingAmtPaymentMode','IsShipped','IsFittingPaid',
                     'distSphericalR','distCylindricalR','distAxisR','distVisionR','AddSphericalR','AddCylindricalR','AddAxisR','AddVisionR','distSphericalL',
                     'distCylindricalL','distAxisL','distVisionL','AddSphericalL','AddCylindricalL','AddAxisL','AddVisionL',
                     'ShippedOnDate','ShippingAmount','GlassFittingAmount'
                     ])
    for obj in Sells:
        b=Brand.objects.get(BrandId=obj.BrandId)
        #p=Prescription.objects.get(Sellid=obj.SellId)
        p=Prescription.objects.filter(Sellid=obj.SellId).first()
        #s=ShippingVendor.objects.get(Sellid=obj.SellId)
        s=ShippingVendor.objects.filter(Sellid=obj.SellId).first()
        #g=GlassFittingVendor.objects.get(Sellid=obj.SellId)
        g=GlassFittingVendor.objects.filter(Sellid=obj.SellId).first()
        if (obj.BrandId==b.BrandId and p is None and s is None and g is None):
             print("in 1")
             writer.writerow([obj.SellId,obj.SoldOnDate,obj.SoldToName,obj.BrandId,b.BrandName,obj.FramePrice,obj.LensPrice,obj.SellingPrice,obj.DiscountPercent,obj.AdvanceAmount,obj.PaymentMode,\
                             obj.RemainingAmount,obj.FullPaymentDone,obj.FullPaymentDate,obj.RemainingAmtPaymentMode,obj.IsShipped,obj.IsFittingPaid,
                             '','','','','','','','','','','','','','','','','','',''
                             ])
        elif(obj.BrandId==b.BrandId and s is None and g is None):
            print("in 2")
            writer.writerow([obj.SellId,obj.SoldOnDate,obj.SoldToName,obj.BrandId,b.BrandName,obj.FramePrice,obj.LensPrice,obj.SellingPrice,obj.DiscountPercent,obj.AdvanceAmount,obj.PaymentMode,\
                             obj.RemainingAmount,obj.FullPaymentDone,obj.FullPaymentDate,obj.RemainingAmtPaymentMode,obj.IsShipped,obj.IsFittingPaid,
                             p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,p.AddVisionR,p.distSphericalL,
                             p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,p.AddAxisL,p.AddVisionL,'','',''

                             ])
        elif(obj.BrandId==b.BrandId and  g is None):
            print("in 3")
            writer.writerow([obj.SellId,obj.SoldOnDate,obj.SoldToName,obj.BrandId,b.BrandName,obj.FramePrice,obj.LensPrice,obj.SellingPrice,obj.DiscountPercent,obj.AdvanceAmount,obj.PaymentMode,\
                             obj.RemainingAmount,obj.FullPaymentDone,obj.FullPaymentDate,obj.RemainingAmtPaymentMode,obj.IsShipped,obj.IsFittingPaid,
                             p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,p.AddVisionR,p.distSphericalL,
                             p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,p.AddAxisL,p.AddVisionL,
                             s.SentOnDate,s.ShippingAmount,''

                             ])

        elif(obj.BrandId==b.BrandId):
            print("in 4")
            writer.writerow([obj.SellId,obj.SoldOnDate,obj.SoldToName,obj.BrandId,b.BrandName,obj.FramePrice,obj.LensPrice,obj.SellingPrice,obj.DiscountPercent,obj.AdvanceAmount,obj.PaymentMode,\
                             obj.RemainingAmount,obj.FullPaymentDone,obj.FullPaymentDate,obj.RemainingAmtPaymentMode,obj.IsShipped,obj.IsFittingPaid,
                             p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,p.AddVisionR,p.distSphericalL,
                             p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,p.AddAxisL,p.AddVisionL,
                             s.SentOnDate,s.ShippingAmount,g.TotalCost
                             ])
    
    return responce

def download_Stock(request):
    Stocks=Stock.objects.all()
    responce=HttpResponse(content_type="text/csv")
    responce['Content-Disposition']='attachment; filename=StockSummary.csv'+str(datetime.now())+'.csv'
    writer=csv.writer(responce, delimiter=','  )
    writer.writerow(['StockId','Date','BrandId','BrandName','Count','PresentCount','PurchasePrice','TotalPurchasedPrice','AssignedPrice','TotalAssignedPrice'])
    for obj in Stocks:
        b=Brand.objects.get(BrandId=obj.BrandId)
        if(obj.BrandId==b.BrandId):
            writer.writerow([obj.StockId,obj.Date,obj.BrandId,b.BrandName,obj.Count,obj.PresentCount,obj.PurchasePrice,obj.TotalPurchasedPrice,obj.AssignedPrice,obj.TotalAssignedPrice])
    return responce

def signout(request):
    print("in logout 1")
    if request.method=="POST":
        print("in logout")
        logout(request)
        return redirect(' ')
    return render(request, "login.html") 

def PrescriptionSummary(request):
    SoldDate=request.POST.get('SoldDate')
    if SoldDate !=None  :
        AllSell=Sell.objects.raw('Select s.Sellid, s.SoldOnDate,s.SoldToName,b.BrandName, s.SellingPrice ,\
        p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,\
        p.AddVisionR,p.distSphericalL,p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,\
        p.AddAxisL,p.AddVisionL,p.TypeOfGlass from optical_sell s join optical_brand b on s.BrandId=b.BrandId\
        join optical_prescription p on s.Sellid=p.Sellid where (s.SoldOnDate == %s)' ,[SoldDate])
    else:
        AllSell=Sell.objects.raw('Select s.Sellid, s.SoldOnDate,s.SoldToName,b.BrandName, s.SellingPrice ,\
        p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,\
        p.AddVisionR,p.distSphericalL,p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,\
        p.AddAxisL,p.AddVisionL,p.TypeOfGlass from optical_sell s join optical_brand b on s.BrandId=b.BrandId\
        join optical_prescription p on s.Sellid=p.Sellid') 
    if request.POST.get("clear"):
        AllSell=Sell.objects.raw('Select s.Sellid, s.SoldOnDate,s.SoldToName,b.BrandName, s.SellingPrice ,\
        p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,\
        p.AddVisionR,p.distSphericalL,p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,\
        p.AddAxisL,p.AddVisionL,p.TypeOfGlass from optical_sell s join optical_brand b on s.BrandId=b.BrandId\
        join optical_prescription p on s.Sellid=p.Sellid')

    return render(request,'PrescriptionSummary.html',{'AllSell':AllSell}) 

def shippingVendor(request):

        Allitems=Sell.objects.raw('Select s.SellId,b.BrandName,s.SoldOnDate,s.SoldToName,s.FramePrice,s.LensPrice, s.SellingPrice\
                                  from optical_sell s join optical_brand b on s.BrandId=b.BrandId\
                                  where IsShipped=False')

        if request.method == "POST": 
            li=[]
            li=request.POST.getlist('sellid')
            print(li)
            for i in li:
                print("i",i)
                s=ShippingVendor()
                s.Sellid=i
                s.SentOnDate= request.POST.get('ShippedOnDate') or datetime.now()
                s.ShippingAmount=request.POST.get('ShipingCost') or None
                s.save()
                Sell1 = Sell.objects.get(SellId=i)
                Sell1.IsShipped =True
                Sell1.save()
                
               

                e=Expenditure()
                e.Sellid=i
                e.SoldOnDate=Sell1.SoldOnDate
                e.SoldToName=Sell1.SoldToName
                travel=ShippingVendor.objects.get(Sellid=i)
                e.SentOnDate=travel.SentOnDate
                e.FramePrice=Sell1.FramePrice
                e.LensPrice=Sell1.LensPrice
                e.SellingPrice=Sell1.SellingPrice
                e.ShippingAmount=travel.ShippingAmount
                #t=Stock.objects.filter(BrandId=Sell1.BrandId,PresentCount__gt=0 ).values('PurchasePrice')
                t=Stock.objects.filter(BrandId=Sell1.BrandId).values('PurchasePrice')
                print("Frame Purchase Price")
                print(t)
                e.FramePurchasePrice=t    
                e.save()


        return render(request,'ShippingVendor.html',{'Allitems':Allitems}) 




def GlassFitting(request):
    Allitems=Sell.objects.raw('Select s.SellId,b.BrandName,s.SoldOnDate,s.SoldToName,si.SentOnDate,s.FramePrice,s.LensPrice,\
    s.SellingPrice,p.distSphericalR,p.distCylindricalR,p.distAxisR,p.distVisionR,p.AddSphericalR,p.AddCylindricalR,p.AddAxisR,\
    p.AddVisionR,p.distSphericalL,p.distCylindricalL,p.distAxisL,p.distVisionL,p.AddSphericalL,p.AddCylindricalL,\
    p.AddAxisL,p.AddVisionL,p.TypeOfGlass\
    from optical_sell s join optical_brand b on s.BrandId=b.BrandId\
    left join optical_prescription p on p.Sellid=s.Sellid\
    join optical_shippingvendor si on s.Sellid=si.Sellid\
    where s.IsShipped=True and isFittingPaid=False')

  
    if request.method == "POST": 
        g=GlassFittingVendor()
        g.Sellid=request.POST.get('submit')
        print("Sellid",g.Sellid)
        g.LensCost=request.POST.get('LensCostSubmit') or None
        g.FittingCost=request.POST.get('FittingCostSubmit') or None
        g.TotalCost=request.POST.get('TotalCostSubmit') or None
        g.EnteredOnDate=datetime.now()
        g.save()
        Sell1 = Sell.objects.get(SellId=g.Sellid)
        Sell1.IsFittingPaid =True
        Sell1.save()

        e=Expenditure.objects.get(Sellid=g.Sellid)
        e.LensCost=g.LensCost
        e.FittingCost= g.FittingCost
        #Ashish will enter only total cost if lens is branded
        e.TotalCost= g.TotalCost or float(e.LensCost)+float(e.FittingCost)
        e.save()


    return render(request,'GlassFittingVendor.html',{"Allitems":Allitems}) 

def expenditureSummary(request):
    FromDate=request.POST.get('FromDate') or None
    ToDate=request.POST.get('ToDate') or None
    print(FromDate)
    '''
    Allitems=Sell.objects.raw('Select s.SellId,b.BrandName,s.SoldOnDate,s.SoldToName,si.SentOnDate,s.FramePrice,s.LensPrice,\
    s.SellingPrice,si.ShippingAmount,g.LensCost,g.FittingCost,g.TotalCost\
    from optical_sell s join optical_brand b on s.BrandId=b.BrandId\
    join optical_shippingvendor si on s.Sellid=si.Sellid\
	join optical_glassfittingvendor g on g.Sellid=s.Sellid\
    where s.IsShipped=True and isFittingPaid=True')
    '''

    if FromDate !=None or ToDate !=None:
        print('in if')
        Allitems= Expenditure.objects.filter(SentOnDate__gte=FromDate, SentOnDate__lte=ToDate)
        data = serializers.serialize("json", Expenditure.objects.filter(SentOnDate__gte=FromDate, SentOnDate__lte=ToDate))
        # Retrieve distinct date and value pairs
        distinct_date_value_pairs = Expenditure.objects.filter(SentOnDate__gte=FromDate, SentOnDate__lte=ToDate).values('SentOnDate', 'ShippingAmount').distinct()
        #Shipdata = serializers.serialize("json", Expenditure.objects.filter(SentOnDate__gte=FromDate, SentOnDate__lte=ToDate).values('SentOnDate', 'ShippingAmount').distinct())
        # Print the results
        
        Sum=0
        for entry in distinct_date_value_pairs:
            print(f"Date: {entry['SentOnDate']}, Value: {entry['ShippingAmount']}")
            Sum=Sum+entry['ShippingAmount']
        print(Sum)
        

    else:
        print('in else')
        Allitems=Expenditure.objects.all()
        data = serializers.serialize("json", Expenditure.objects.all())
         # Retrieve distinct date and value pairs
        distinct_date_value_pairs = Expenditure.objects.values('SentOnDate', 'ShippingAmount').distinct()
        #Shipdata = serializers.serialize("json", Expenditure.objects.values('SentOnDate', 'ShippingAmount').distinct())
        # Print the results
        
        Sum=0
        for entry in distinct_date_value_pairs:
            print(f"Date: {entry['SentOnDate']}, Value: {entry['ShippingAmount']}")
            Sum=Sum+entry['ShippingAmount']
        print(Sum)
        

    #data = serializers.serialize("json", Expenditure.objects.all())
    
    return render(request,'ExpenditureSummary.html',{'Allitems':Allitems,"data":data,"shippingExpt":Sum}) 

