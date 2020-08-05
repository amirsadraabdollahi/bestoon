from django.shortcuts import render
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from web.models import User, Expense, Income, Token
from datetime import datetime

# Create your views here.
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

