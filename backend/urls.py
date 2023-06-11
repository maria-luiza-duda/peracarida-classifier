from django.urls import path
from . import views

urlpatterns = [
    path('registerrecord/', views.register, name='registerrecord'),
    path('home/', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('results/', views.results, name='results'),
    path('download-chart/', views.download_chart, name='download_chart'),

]

