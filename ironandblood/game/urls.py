from django.conf.urls import url

from . import views

USERNAME_REGEX = '(?=.{8,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])'

app_name = 'game'
urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^exchanges$', views.exchanges, name='exchanges'),
    url(r'^exchanges/(?P<exchange_pk>[0-9]+)', views.update_exchange, name='update_exchange'),
    url(r'^exchanges/(?P<offeree>.+)', views.new_exchange, name='exchange'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
]

