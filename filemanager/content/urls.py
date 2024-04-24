from django.urls import path

from . import views


app_name='content'

urlpatterns= [
    path('add/',views.add_content,name='add'),
]