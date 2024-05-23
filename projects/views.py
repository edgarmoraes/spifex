from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Project

def projects(request):
    return render(request, 'projects.html')

def save_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_code = request.POST.get('project_id')
        project_type = request.POST.get('project_type')
        project_description = request.POST.get('project_description')

        project = Project(
            project_name=project_name,
            project_code=project_code,
            project_type=project_type,
            project_description=project_description
        )
        project.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})