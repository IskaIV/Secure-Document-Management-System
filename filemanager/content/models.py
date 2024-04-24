from django.db import models

from account.models import User

import uuid

from project.models import Project

# Create your models here.


class Content(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    project=models.ForeignKey(Project,related_name='content',on_delete=models.CASCADE)
    name=models.CharField(max_length=255)
    description=models.TextField(blank=True,null=True)
    created_by=models.ForeignKey(User, related_name='content',on_delete=models.CASCADE)
    
    
    def __str__(self):
        return self.name
    
