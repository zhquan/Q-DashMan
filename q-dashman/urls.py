"""tfm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))

from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]
"""

from django.conf.urls import url
from django.contrib import admin

from dashboard import views


urlpatterns = [
    url(r'^$', views.index),
    url(r'^upload_projects', views.upload_projects),
    url(r'^upload_setup', views.upload_setup),
    url(r'^add_orgs', views.add_orgs),
    url(r'^add_slack', views.add_slack),
    url(r'^add_meetup', views.add_meetup),
    url(r'^add_repo', views.add_repo),
    url(r'^rm_repo', views.rm_repo),
    url(r'^generate_dashboard', views.generate_dashboard),
    url(r'^generate_stop', views.dash_stop),
    url(r'^conf_setup', views.conf_setup),
    url(r'^conf_backend', views.conf_backend),
    url(r'^conf_study', views.conf_study),
    url(r'^rm_backend', views.rm_backend),
    url(r'^rm_study', views.rm_study),
    url(r'^admin/', admin.site.urls),

    #url(r'^posts$', views.projects_upload),

]
