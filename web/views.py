# -*- coding:utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Expense, Income, Token
from datetime import datetime

# Create your views here.
random_str = lambda N: ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(N))


@RateLimited(4)
def register(request):
    if request.POST.has_key('requestcode'): #form is filled. if not spam, generate code and save in db, wait for email confirmation, return message
        logger.debug("def register requestcode: " + format(request.POST))
        #is this spam? check reCaptcha
        if not grecaptcha_verify(request): # captcha was not correct
            context = {'message': 'کپچای گوگل درست وارد نشده بود. شاید ربات هستید؟ کد یا کلیک یا تشخیص عکس زیر فرم را درست پر کنید. ببخشید که فرم به شکل اولیه برنگشته!'} #TODO: forgot password
            return render(request, 'register.html', context)

        if User.objects.filter(email = request.POST['email']).exists(): # duplicate email
            context = {'message': 'متاسفانه این ایمیل قبلا استفاده شده است. در صورتی که این ایمیل شما است، از صفحه ورود گزینه فراموشی پسورد رو انتخاب کنین. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)

        if not User.objects.filter(username = request.POST['username']).exists(): #if user does not exists
                code = random_str(28)
                now = datetime.now()
                email = request.POST['email']
                password = make_password(request.POST['password'])
                username = request.POST['username']
                temporarycode = Passwordresetcodes (email = email, time = now, code = code, username=username, password=password)
                temporarycode.save()
                message = PMMail(api_key = settings.POSTMARK_API_TOKEN,
                subject = "فعال سازی اکانت بستون",
                sender = "abdollahiamirsadra@gmail.com",
                to = email,
                text_body = "برای فعال سازی اکانت بستون خود روی لینک روبرو کلیک کنید: http://todoer.ir/accounts/register/?email={}&code={}".format(email, code),
                tag = "account request")
                message.send()
                context = {'message': 'ایمیلی حاوی لینک فعال سازی اکانت به شما فرستاده شده، لطفا پس از چک کردن ایمیل، روی لینک کلیک کنید.'}
                return render(request, 'login.html', context)
        else:
            context = {'message': 'متاسفانه این نام کاربری قبلا استفاده شده است. از نام کاربری دیگری استفاده کنید. ببخشید که فرم ذخیره نشده. درست می شه'} #TODO: forgot password
            #TODO: keep the form data
            return render(request, 'register.html', context)
    elif request.GET.has_key('code'): # user clicked on code
        logger.debug("def register code: " + format(request.GET))
        email = request.GET['email']
        code = request.GET['code']
        if Passwordresetcodes.objects.filter(code=code).exists(): #if code is in temporary db, read the data and create the user
            new_temp_user = Passwordresetcodes.objects.get(code=code)
            newuser = User.objects.create(username=new_temp_user.username, password=new_temp_user.password, email=email)
            this_token = random_str(48)
            token = Token.objects.create(user = newuser, token = this_token)
            Passwordresetcodes.objects.filter(code=code).delete() #delete the temporary activation code from db
            context = {'اکانت شما ساخته شد. توکن شما {} است . آن را ذخیره کنید'.format(this_token)}
            return render(request, 'login.html', context)
        else:
            context = {'message': 'این کد فعال سازی معتبر نیست. در صورت نیاز دوباره تلاش کنید'}
            return render(request, 'login.html', context)
    else:
        context = {'message': ''}
        return render(request, 'register.html', context)

@csrf_exempt
def submit_expense(request) :
    print(request.POST)
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    this_amount = request.POST['amount']
    this_text  = request.POST['text']
    this_date = datetime.now()
    if('date' in request.POST):
        this_date=request.POST['date']
    Income.objects.create(user = this_user, date = this_date, amount = this_amount, text = this_text)
    return JsonResponse({
        'status':'ok' ,
        }, encoder=json.JSONEncoder)
@csrf_exempt
def submit_expense(request) :
    print(request.POST)
    this_token = request.POST['token']
    this_user = User.objects.filter(token__token = this_token).get()
    this_amount = request.POST['amount']
    this_text  = request.POST['text']
    this_date = datetime.now()
    if('date' in request.POST):
        this_date=request.POST['date']
    Expense.objects.create(user = this_user, date = this_date, amount = this_amount, text = this_text)
    return JsonResponse({
        'status':'ok' ,
        }, encoder=json.JSONEncoder)

