from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = 'frontend'

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('registerrecord/', views.RegisterRecordView.as_view(), name='registerrecord'),  # Alteração nesta linha
    path('upload/', views.UploadView.as_view(), name='upload'),
    path('results/', views.ResultsView.as_view(), name='results'),
    path('analyze/<str:temp_path>/', views.AnalyzeView.as_view(), name='analyze')
] 

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
