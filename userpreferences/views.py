from django.shortcuts import render
import os
import json
from django.conf import settings
import pdb
from .models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect



# Create your views here.


def index(request):
    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preference = None

    currency_data = []

    #get the path of currency json file
    file_path = os.path.join(settings.BASE_DIR,'currencies.json')
    # pdb.set_trace()
    # open() # takes a file, we can write, append or read it

    with open(file_path,'r')  as json_file: # r is for read

        data = json.load(json_file)

        for key,value in data.items():
            currency_data.append({'name':key,'value':value})

    if exists:
        user_preference = UserPreference.objects.get(user=request.user)

    if request.method == "GET":

    # pdb.set_trace()


        return render(request,'preferences/index.html',{'currencies':currency_data,'user_preference':user_preference})

    else:
        currency = request.POST['currency']
        if exists:

            user_preference.currency = currency
            user_preference.save()

        else:
            UserPreference.objects.create(user = request.user, currency = currency)
        messages.success(request,'Changes saved to ' + currency)
        return render(request,'preferences/index.html',{'currencies':currency_data,'user_preference':user_preference})


