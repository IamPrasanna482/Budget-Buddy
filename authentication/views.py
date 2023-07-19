from django.shortcuts import render,redirect
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


from django.utils.encoding import force_bytes,DjangoUnicodeDecodeError,force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import token_generator
import threading

from django.contrib import auth

from django.urls import reverse
# Create your views here.

class EmailThread(threading.Thread):
    def __init__(self,email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently = False)



class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']


        if not validate_email(email):
            return JsonResponse({'email_error':"Email is INVALID."},status=400)  # 400 -> invalid

        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Email already exists!! Choose another one'},status=409)  # 409 -> already exists

        return JsonResponse({'email_valid':True})



class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']


        if not str(username).isalnum():
            return JsonResponse({'username_error':"Username is INVALID. It can't contain symbols."},status=400)  # 400 -> invalid

        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Username already exists!! Choose another one'},status=409)  # 409 -> already exists

        return JsonResponse({'username_valid':True})

class RegistrationView(View):
    def get(self, request):
        return render(request,'authentication/register.html')

    def post(self, request):
        # get user data

        # validate

        #create a user account

        username =  request.POST['username']
        email =  request.POST['email']
        password =  request.POST['password']

        context = {
            'fieldValues':request.POST
        }

        if not User.objects.filter(username=username).exists(): # check in db
            if not User.objects.filter(email=email).exists():

                if len(password) < 6:
                    messages.error(request,'Password is too short')
                    return render(request,'authentication/register.html',context)

                    #save the user
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)

                user.is_active = False
                user.save()


                # path to view
                # for activation link, 1. getting the domain we are on
                # 2. relative url to verification
                # 3. encode uid
                # 4. get the token to verify

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                domain = get_current_site(request).domain

                link = reverse('activate',kwargs={'uidb64':uidb64, 'token':token_generator.make_token(user)})

                email_subject = 'Activate your Budget Buddy Account'

                activate_url = 'http://' + domain + link

                email_body = 'Hi ' + user.username + '\n Please use the following link to verify your account ! ' + activate_url
                email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@semicolon.com',
                    [email],
                )

                EmailThread(email).start()
                # email.send(fail_silently=False)
                messages.success(request,'Account successfully created !')
                return render(request,'authentication/register.html')

        return render(request,'authentication/register.html')

class VerificationView(View):

    def get(self, request,uidb64,token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)
        except(TypeError,ValueError,OverflowError,User.DoesNotExist):
            user = None

        if user is not None and token_generator.check_token(user,token):
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect("login")

        elif not token_generator.check_token(user,token):
            messages.warning(request,'User Already Activated')
            return redirect("login")

        elif user.is_active:
            return redirect('login')

        else:
            messages.error(request,"Activation Link is Invalid")
            return redirect("login")

class LoginView(View):
    def get(self, request):
        return render(request,'authentication/login.html')

    def post(self,request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:

            user = auth.authenticate(username=username,password = password)

            if user:
                if  user.is_active:
                    # login the user
                    print(1234)
                    auth.login(request,user)
                    messages.success(request,'Welcome, ' + user.username + '. You are now logged in !')
                    return redirect('expenses')



                messages.error(request, 'Account is not activated! Please check you Email')
                return render(request,'authentication/login.html')

            messages.error(request, 'Invalid credentials! Please try again')
            return render(request,'authentication/login.html')

        messages.error(request, 'Please fill all the fields')
        return render(request,'authentication/login.html')


class LogoutView(View):
    def post(self,request):
        #logout the user
        auth.logout(request)
        messages.success(request,'You have been logged out')
        return redirect('login')

class RequestPasswordResetEmail(View):
    def get(self,request):
       return render(request,'authentication/reset-password.html')

    def post(self,request):
       email = request.POST["email"]

       context = {
        'values': request.POST
       }

       if not validate_email(email):
           messages.error(request,'Please enter a valid email address')

       user = User.objects.filter(email=email)
       current_site = get_current_site(request)

       if user.exists():
        email_contents = {
        'user':user[0],
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
        'token': PasswordResetTokenGenerator().make_token(user[0]),
       }
       link = reverse('reset-user-password',kwargs={'uidb64':email_contents['uid'], 'token':email_contents['token']})
       email_subject = 'Password Reset Instructions'

       reset_url = 'http://' + current_site.domain + link

       email_body = 'Hi' + '\n Please use the following link to reset your  password ! ' + reset_url
       email = EmailMessage(
                    email_subject,
                    email_body,
                    'noreply@semicolon.com',
                    [email],
                )

       EmailThread(email).start()
    #    email.send(fail_silently=False)
       messages.success(request,'We have sent you an Email to reset your password')


       return render(request,'authentication/reset-password.html')


class CompletePasswordReset(View):
    def get(self,request,uidb64,token):


        context = {
            'uidb64' : uidb64,
            'token' : token
        }
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,'Password Link is Invalid, Please request a new one')
            return render(request,'authentication/reset-password.html')




        except Exception as identifier:
            return render(request,'authentication/set-new-password.html',context)

    def post(self,request,uidb64,token):
        context = {
            'uidb64' : uidb64,
            'token' : token
        }

        password = request.POST['password']
        password2 = request.POST['password2']

        if password != password2:
            messages.error(request, 'Passwords dont match')
            return render(request,'authentication/set-new-password.html',context)

        if len(password) < 6:
            messages.error(request, 'Passwords too short')
            return render(request,'authentication/set-new-password.html',context)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password = password
            user.save()
            messages.success(request,'Password Reset Successfully, you can login now with your new password')
            return redirect('login')
        except Exception as identifier:
            messages.info(request,'Something went wrong, Try again later')
            return render(request,'authentication/set-new-password.html',context)


        # return render(request,'authentication/set-new-password.html',context)

