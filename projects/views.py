import uuid
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Projects

def projects(request):
    if request.method =="GET":
        projects_list = Projects.objects.all().order_by('id')

        context = {
            'Projects_list': projects_list,
        }
        return render(request, 'projects.html', context)

def save_project(request):
    if request.method == 'POST':
        project_name = request.POST.get('project_name')
        project_code = request.POST.get('project_id')
        project_type = request.POST.get('project_type')
        project_description = request.POST.get('project_description')
        uuid_project = uuid.uuid4()

        project = Projects(
            project_name=project_name,
            project_code=project_code,
            project_type=project_type,
            project_description=project_description,
            uuid_project=uuid_project
        )
        project.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

