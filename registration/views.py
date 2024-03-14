from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required(login_url='login')
def HomePage(request):
    return render(request, 'home.html')

def SignupPage(request):
    if request.method=='POST':
        uname=request.POST.get('username')
        email=request.POST.get('email')
        password1=request.POST.get('password1')
        password2=request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Your passwords do not match.")
            return render(request, 'signup.html', {'username': uname, 'email': email})
        else:

            my_user=User.objects.create_user(uname,email,password1)
            my_user.save()
            return redirect('login')

    return render(request, 'signup.html')

def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password1=request.POST.get('password')

        if not username:
            messages.error(request, "Please fill in the username field.")
            return render(request, 'login.html')
    
        user = authenticate(request, username=username, password=password1)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Your username or password is incorrect.")
            return render(request, 'login.html')
        
    return render(request, 'login.html')

def LogoutPage(request):
    logout(request)
    return redirect('login')