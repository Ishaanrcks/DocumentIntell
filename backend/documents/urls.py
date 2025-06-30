from django.urls import path
from . import views

urlpatterns = [
    path('documents/', views.get_documents),
    path('documents/upload/', views.upload_document),
    path('documents/query/', views.query_document),
    # path('debug/', views.debug_status),

]
