from django.shortcuts import render

def projects(request):
    return render(request, 'projects.html')

def save_project(request):
    return render(request, 'projects.html')