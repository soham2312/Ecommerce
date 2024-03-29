from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login
from accounts.models import *
from django.http import HttpResponse
from products.models import *
from django.http import HttpResponseRedirect
import razorpay
from django.conf import settings


# Create your views here.
def login_page(request):
    if(request.method=='POST'):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)
        if not user_obj.exists():
            messages.warning(request,'Account not found')
            return HttpResponseRedirect(request.path_info)
        
        if not user_obj[0].profile.is_email_verified:
            messages.warning(request,'Your account is not verified')
            return HttpResponseRedirect(request.path_info)
        
        user_obj= authenticate(username=email,password=password)

        if user_obj:
            login(request,user_obj)
            return redirect('/')
        
        messages.warning(request,'InValid Credentials')
        return HttpResponseRedirect(request.path_info)
    return render(request,'accounts/login.html')

def register_page(request):
    if(request.method == 'POST'):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=email)
        if user_obj.exists():
            messages.warning(request,'User already exists')
            return HttpResponseRedirect(request.path_info)
        user_obj= User.objects.create(first_name=first_name,last_name=last_name,email=email,username=email)
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request,'Email has been sent.')
        return HttpResponseRedirect(request.path_info)
    
    return render(request,'accounts/register.html')

def remove_cart(request,cart_item_uid):
    try:
        cart_item=Cartitems.objects.get(uid=cart_item_uid)
        cart_item.delete()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def cart(request):
    cart_obj=None
    try:
        cart_obj=Cart.objects.get(user=request.user,is_paid=False)
    except Exception as e:
        print(e)

    print(cart_obj)
    if request.method=='POST':
        coupon=request.POST.get('coupon')
        coupon_obj=Coupon.objects.filter(coupon_code__icontains=coupon)
        if not coupon_obj.exists():
            messages.warning(request,'Invalid Coupon')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if cart_obj.coupon:
            messages.warning(request,'Coupon already applied')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if cart_obj.get_cart_total()<coupon_obj[0].minimum_amount:
            messages.warning(request,'Minimum amount should be {} to gain discounts'.format(coupon_obj[0].minimum_amount))
        #     return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        if coupon_obj[0].is_expired:
            messages.warning(request,'Coupon already expired')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        cart_obj.coupon=coupon_obj[0]
        cart_obj.save()

        messages.success(request,'Coupon applied successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    payment=None
    if cart_obj:
        client=razorpay.Client(auth=(settings.KEY,settings.KEY_SECRET))

        payment=client.order.create({'amount':cart_obj.get_cart_total()*100,'currency':'INR','payment_capture':'1'})
        cart_obj.razorpay_order_id=payment['id']

        cart_obj.save()
    # payment=None

    context={'cart':cart_obj,'payment':payment}
    return render(request,'accounts/cart.html',context=context)

def activate_email(request , email_token):
    try:
        user = Profile.objects.get(email_token= email_token)
        user.is_email_verified = True
        user.save()
        return redirect('/')
    except Exception as e:
        return HttpResponse('Invalid Email token')
    
def add_to_cart(request,uid):
    variant=request.GET.get('size')
    product=Product.objects.get(uid=uid)
    user=request.user
    cart,_=Cart.objects.get_or_create(user=user,is_paid=False)
    cart_item=Cartitems.objects.create(cart=cart,product=product)

    if variant:
        variant=request.GET.get('size')
        size=SizeVariant.objects.get(size_name=variant)
        cart_item.size=size
        cart_item.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_coupon(request,cart_id):
    cart_obj=Cart.objects.get(uid=cart_id)
    cart_obj.coupon=None
    cart_obj.save()
    messages.success(request,'Coupon removed successfully')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def success(request):
    order_id=request.GET.get('order_id')
    cart=Cart.objects.get(razorpay_order_id=order_id)
    cart.is_paid=True
    cart.save()
    return HttpResponse('Payment Success')
