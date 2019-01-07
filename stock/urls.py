"""portfolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path
from mainapp.views import get_index,get_hello
from stocks.views import get_stocks,get_add,post_add,post_stocks,get_plot,get_plot_api,get_add_api,get_stocks_api
from django.conf.urls.static import static
from django.views.generic.base import RedirectView


urlpatterns = [
    path('^favicon\.ico$',RedirectView.as_view(url='/static/icon/growth.ico')),
    # path('admin/', admin.site.urls),
    path('index', get_index),
    path('hello', get_hello),
    path('stocks', get_stocks),
    path('add', get_add),
    path('add/post', post_add),
    path('add/api', get_add_api),
    path('stocks/post', post_stocks),
    path('plot_test', get_plot),
    path('api/plot', get_plot_api),
    path('stocks/api', get_stocks_api),
]
