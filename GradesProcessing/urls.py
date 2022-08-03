from django.urls import path,include

from . import views
import GradesProcessing

urlpatterns = [
   
    path('gphome',views.gp_home, name='gphome'),
     path('gphome1',views.gp_home1, name='gphome1'),
]