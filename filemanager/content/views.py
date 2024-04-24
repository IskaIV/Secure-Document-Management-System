from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from project.models import Project

# Create your views here.

from . models import Content



@login_required
def add_content(request,project_id):
    project=Project.objects.filter(created_by=request.user).get(pk=project_id)
    
    if request.method == 'POST':
        name=request.POST.get('name','')
        description=request.POST.get('description','')
        
        if name:
            Content.objects.create(project=project,name=name,description=description)
            return redirect(f'/projects/{project_id}/')
        
    return render(request,"content/add.html",{
        'project':project
    })
    