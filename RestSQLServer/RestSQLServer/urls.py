"""RestSQLServer URL Configuration

The `urlpatterns` list routes URLs to views.py. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views.py
    1. Add an import:  from my_app import views.py
    2. Add a URL to urlpatterns:  path('', views.py.home, name='home')
Class-based views.py
    1. Add an import:  from other_app.views.py import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.test),
    # 作为restsql Http接口
    path('restsql/query', views.api_query),
    path('restsql/find_tables', views.table_query),
    path('restsql/find_databases', views.database_query),
    # 作为restsql Grafana接口
    path('query', views.grafana_query),
    path('search', views.grafana_search),
    path('find_options', views.grafana_options),
    path('find_tables', views.grafana_tables),
]
