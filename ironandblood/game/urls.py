from django.conf.urls import url

from . import views

app_name = 'game'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^exchanges$', views.exchanges, name='exchanges'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
]

