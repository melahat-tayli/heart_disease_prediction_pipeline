"""Visualizer URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from pathlib import Path

import bokeh
from bokeh.server.django import autoload, directory, static_extensions
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path

from . import views

bokeh_app_config = apps.get_app_config("bokeh.server.django")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("visualization/", views.visualization),
]

base_path = settings.BASE_PATH

bokeh_apps = [autoload("visualization", views.visualization_handler)]

apps_path = Path(bokeh.__file__).parent.parent / "examples" / "app"
bokeh_apps += directory(apps_path)

urlpatterns += static_extensions()
urlpatterns += staticfiles_urlpatterns()
