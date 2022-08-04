"""AWSP URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from AWSP import views
from django.urls import path, include

urlpatterns = [
    path('', views.index, name='index'),
    path('admin/', admin.site.urls),
    path('UGPG', views.ug_pg, name='UGPG'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('Transcripts/', include('Transcripts.urls')),
    path('Registrations/',include('Registrations.urls')),
    #path('CoordinatorDB/',include('CoordinatorDB.urls')),
    path('BTExamStaffDB/', include('BTExamStaffDB.urls')),
    path('BTsuperintendent/', include('BTsuperintendent.urls')),
    path('BTfaculty/', include('BTfaculty.urls')),
    path('BThod/', include('BThod.urls')),
    path('BTco_ordinator/', include('BTco_ordinator.urls')),

    path('MTExamStaffDB/', include('MTExamStaffDB.urls')),
    path('MTsuperintendent/', include('MTsuperintendent.urls')),
    path('MTfaculty/', include('MTfaculty.urls')),
    path('MThod/', include('MThod.urls')),
    path('MTco_ordinator/', include('MTco_ordinator.urls')),

    path('SupExamDB/',include('SupExamDB.urls')), 
    path('SupExamDBRegistrations/',include('SupExamDBRegistrations.urls')),
    path('SupExamDBRegistrationStatus/',include('SupExamDBRegistrationStatus.urls')),
    path('GradesProcessing/',include('GradesProcessing.urls')),
    path('home', views.home, name='home'),

]

