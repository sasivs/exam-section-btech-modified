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
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('Transcripts/', include('Transcripts.urls')),
    path('Registrations/',include('Registrations.urls')),
    #path('CoordinatorDB/',include('CoordinatorDB.urls')),
    path('ExamStaffDB/', include('ExamStaffDB.urls')),
    path('superintendent/', include('superintendent.urls')),
    path('faculty/', include('faculty.urls')),
    path('hod/', include('hod.urls')),
    path('co_ordinator/', include('co_ordinator.urls')),
    path('SupExamDB/',include('SupExamDB.urls')),
    path('SupExamDBRegistrations/',include('SupExamDBRegistrations.urls')),
    path('SupExamDBRegistrationStatus/',include('SupExamDBRegistrationStatus.urls')),
    path('GradesProcessing/',include('GradesProcessing.urls')),
    path('home', views.home, name='home'),

]

